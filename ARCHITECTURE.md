# Architecture — Hostel Counselling Backend

## Table of Contents

1. [System Overview](#1-system-overview)
2. [Tech Stack](#2-tech-stack)
3. [Project Structure](#3-project-structure)
4. [How the System Works](#4-how-the-system-works)
   - [Authentication Flow](#41-authentication-flow)
   - [Counselling / Allocation Flow](#42-counselling--allocation-flow)
   - [Friend Requests](#43-friend-requests)
5. [Database Tables](#5-database-tables)
   - [User](#51-user)
   - [Rooms](#52-rooms)
   - [RoomAssignments](#53-roomassignments)
   - [Preference](#54-preference)
   - [CounsellingSession](#55-counsellingsession)
   - [TurnQueue & ProcessingQueue](#56-turnqueue--processingqueue)
   - [Friendship](#57-friendship)
6. [Enum Types](#6-enum-types)
7. [API Modules](#7-api-modules)
8. [Database Indexes](#8-database-indexes)
9. [Migration History](#9-migration-history)
10. [Known Issues & TODOs](#10-known-issues--todos)

---

## 1. System Overview

This is the backend for a **hostel room counselling system** — a process where students are assigned a rank (based on merit/CGPA or similar criteria) and are called **one by one** in rank order to pick their preferred hostel room during a live session.

```
                        ┌─────────────────────────────────────┐
                        │         Frontend (React/Vite)        │
                        │   localhost:5173 / Vercel deploy     │
                        └───────────────┬─────────────────────┘
                                        │ HTTPS + Bearer Token
                        ┌───────────────▼─────────────────────┐
                        │       FastAPI Backend (Python)       │
                        │       api.py  +  sub-routers         │
                        └───┬───────────────────┬─────────────┘
                            │                   │
              ┌─────────────▼───┐   ┌───────────▼───────────┐
              │  Firebase Admin │   │  PostgreSQL Database   │
              │  (Token verify) │   │  (psycopg2 + Render)  │
              └─────────────────┘   └───────────────────────┘
```

---

## 2. Tech Stack

| Component      | Technology                  |
|----------------|-----------------------------|
| Language       | Python 3                    |
| Framework      | FastAPI 0.104.1             |
| ASGI Server    | Uvicorn                     |
| Database       | PostgreSQL                  |
| DB Driver      | psycopg2-binary             |
| Authentication | Firebase Admin SDK 6.2      |
| Validation     | Pydantic v2                 |
| Hosting        | Render (production)         |
| Containerized  | Docker                      |

---

## 3. Project Structure

```
hostel-counselling-backend/
│
├── api.py                   ← Main FastAPI app, CORS config, ~30 core endpoints
├── allocation.py            ← Allocation session engine (admin + user turn logic)
├── firebase_auth.py         ← Firebase auth router & token verification helper
├── friend_requests.py       ← Friend request endpoints (registration-number based)
├── config.py                ← DB config loader (env vars / DATABASE_URL)
├── make_admin.py            ← Utility: promote a user to admin by email
│
├── dbconfig/                ← Data Access Layer (one file per domain)
│   ├── __init__.py
│   ├── _db_helper.py        ← Shared get_connection() helper
│   ├── user.py              ← User CRUD
│   ├── room.py              ← Room / hostel / block / floor queries
│   ├── preference.py        ← Preference CRUD
│   ├── friendship.py        ← Friendship CRUD (legacy lower-level)
│   ├── counselling_session.py  ← Session queries
│   └── queue_management.py    ← Turn/processing queue queries
│
├── migrations/              ← Sequential SQL migration files
│   ├── 000_initial_schema.sql
│   ├── 001_add_counselling_system.sql
│   ├── 002_add_firebase_auth.sql
│   ├── 003_cleanup_user_table.sql
│   ├── 004_add_user_role.sql
│   ├── 005_denormalize_to_rooms_table.sql
│   ├── 006_add_room_assignments_table.sql
│   └── 007_add_allocated_room_to_user.sql
│
├── sample_rooms_data.sql    ← Seed data for rooms
├── Dockerfile               ← Production container definition
├── .env.example             ← Template for required environment variables
└── requirements.txt         ← Python dependencies
```

---

## 4. How the System Works

### 4.1 Authentication Flow

All protected endpoints require a **Firebase Bearer token** in the `Authorization` header.

```
Client
  │
  ├─► POST /api/auth/firebase  {firebaseUid, email, displayName}
  │         │
  │         ├── verify_firebase_token() checks token with Firebase Admin SDK
  │         ├── If user exists → UPDATE lastLoginAt
  │         └── If new user   → INSERT with rank=999999, gender='other' (update later)
  │
  ├─► GET  /api/auth/me              ← get current user profile
  └─► PATCH /api/auth/me             ← update registrationNumber / displayName
```

Firebase credentials are loaded from:
- **Production**: `FIREBASE_SERVICE_ACCOUNT_BASE64` env var (base64-encoded JSON)
- **Local dev**: `serviceAccountKey.json` file

---

### 4.2 Counselling / Allocation Flow

This is the core feature. An admin starts a session, and students are called in rank order to pick a room.

```
ADMIN                                     STUDENT (rank N)
  │                                              │
  ├── POST /api/allocation/session/start         │
  │        Creates CounsellingSession            │
  │        Sets currentRank = 1                 │
  │        Starts background auto-advance task   │
  │                                              │
  │         ┌──────────────────────────────┐     │
  │         │  AllocationAutoAdvance loop  │     │
  │         │  Polls every 2 seconds       │     │
  │         │  If elapsed >= turnDuration  │     │
  │         │    → advance currentRank     │     │
  │         └──────────────────────────────┘     │
  │                                              │
  │                           GET /api/allocation/session/current
  │                                Polls for their turn
  │                                (currentRank == user.rank?)
  │                                              │
  │                           POST /api/allocation/select-room
  │                                {roomId: 42}
  │                                    │
  │                                    ├── verify it's user's turn
  │                                    ├── check room not locked & not full
  │                                    ├── check user not already assigned
  │                                    ├── INSERT into RoomAssignments
  │                                    ├── UPDATE User.allocatedRoomId
  │                                    ├── UPDATE Rooms.occupied += 1
  │                                    └── ADVANCE to next rank immediately
  │
  ├── POST /api/allocation/session/pause
  ├── POST /api/allocation/session/resume
  ├── POST /api/allocation/session/next-rank   ← skip current user manually
  └── POST /api/allocation/session/stop
           Marks session 'completed'
           Clears RoomAssignments, Preferences, room states
```

**Auto-advance** is handled by `AllocationAutoAdvance` — a singleton asyncio background task that wakes every 2 seconds and checks if the current user's `turnDuration` has elapsed. If so, it moves to the next rank automatically.

---

### 4.3 Friend Requests

Students can add friends by **registration number** (not user ID). This is mainly a social layer (roommate coordination).

```
POST /api/friends/request   {receiverRegistrationNumber: "21BCS001"}
  │
  ├── verify token → get current user
  ├── look up receiver by registrationNumber
  ├── check for existing friendship (either direction)
  │     pending  → error: already pending
  │     accepted → error: already friends
  │     rejected → re-activate (set to pending again)
  └── INSERT into Friendship (status='pending')

POST /api/friends/request/{id}/accept   → UPDATE status='accepted'
POST /api/friends/request/{id}/reject   → UPDATE status='rejected'
GET  /api/friends                       → list of accepted friends
GET  /api/friends/requests/pending      → incoming pending requests (with sender info)
GET  /api/friends/requests              → all sent + received requests
```

---

## 5. Database Tables

### 5.1 `User`

The central table. Every student who logs in via Firebase gets a row here.

| Column               | Type        | Description |
|----------------------|-------------|-------------|
| `id`                 | SERIAL PK   | Internal user ID |
| `firebaseUid`        | VARCHAR     | Firebase Auth UID (unique) |
| `email`              | VARCHAR     | User email (unique) |
| `displayName`        | VARCHAR     | Display name from Firebase |
| `registrationNumber` | VARCHAR     | College registration number (unique) |
| `gender`             | ENUM        | `male`, `female`, `other` |
| `rank`               | INTEGER     | Counselling rank (lower = earlier turn) |
| `hostel`             | VARCHAR     | Preferred/assigned hostel |
| `role`               | ENUM        | `user` (default) or `admin` |
| `isActive`           | BOOLEAN     | Whether account is active |
| `allocatedRoomId`    | FK → Rooms  | Room allocated during counselling |
| `allocatedAt`        | TIMESTAMP   | When the room was allocated |
| `lastLoginAt`        | TIMESTAMP   | Last Firebase login time |
| `createdAt`          | TIMESTAMP   | Account creation time |

**Indexes:** `rank`, `role`, `allocatedRoomId`

---

### 5.2 `Rooms`

A **denormalized flat table** representing every room in every hostel. Instead of separate `Hostel`, `Block`, `Floor` tables, all that info is stored as columns on every row.

| Column           | Type      | Description |
|------------------|-----------|-------------|
| `id`             | SERIAL PK | Room ID |
| `roomNumber`     | VARCHAR   | e.g. `"101"`, `"B204"` |
| `floorNumber`    | INTEGER   | Which floor |
| `blockName`      | VARCHAR   | e.g. `"A"`, `"B"`, `"New Block"` |
| `hostelName`     | VARCHAR   | e.g. `"Boys Hostel 1"` |
| `isAC`           | BOOLEAN   | Air-conditioned room? |
| `isDeluxe`       | BOOLEAN   | Deluxe room? |
| `isApartment`    | BOOLEAN   | Apartment-style? |
| `capacity`       | INTEGER   | Max occupants (2–6) |
| `occupied`       | INTEGER   | Current occupant count |
| `availableSlots` | INTEGER   | **Computed**: `capacity - occupied` |
| `isLocked`       | BOOLEAN   | Temporarily locked during a turn |
| `lockedByUserId` | FK → User | Who locked it |
| `lockedAt`       | TIMESTAMP | When it was locked |
| `lockExpiresAt`  | TIMESTAMP | When the lock expires |
| `assignedUserId` | FK → User | ⚠️ Deprecated — use `RoomAssignments` |
| `assignedAt`     | TIMESTAMP | ⚠️ Deprecated |
| `createdAt`      | TIMESTAMP | — |
| `updatedAt`      | TIMESTAMP | Auto-updated by trigger |

**Unique constraint:** `(hostelName, blockName, floorNumber, roomNumber)`

**Indexes:** `hostelName`, `blockName`, `availableSlots` (partial, where > 0), `isLocked`, `assignedUserId`

> **Why denormalized?** Originally there were separate `Hostel`, `Block`, `Floor`, `Room` tables (migration 000). Migration 005 collapsed them all into `Rooms` for simpler querying and faster reads.

---

### 5.3 `RoomAssignments`

Tracks which users are assigned to which rooms. Supports **multiple students per room** (up to `capacity`).

| Column       | Type         | Description |
|--------------|--------------|-------------|
| `id`         | SERIAL PK    | — |
| `roomId`     | FK → Rooms   | The room |
| `userId`     | FK → User    | The student |
| `assignedAt` | TIMESTAMP    | When assigned |

**Constraints:**
- `UNIQUE(userId)` → a student can only be assigned to **one** room
- `UNIQUE(roomId, userId)` → no duplicate assignments

**Indexes:** `roomId`, `userId`

> This table is the **source of truth** for assignments. `User.allocatedRoomId` is a denormalized fast-lookup copy.

---

### 5.4 `Preference`

Stores a student's room selection preference (what room they chose during counselling).

| Column           | Type       | Description |
|------------------|------------|-------------|
| `id`             | SERIAL PK  | — |
| `userId`         | FK → User  | The student |
| `preferenceRank` | INTEGER    | 1–5 priority (1 = top choice) |
| `roomId`         | FK → Rooms | The preferred room |
| `isAnyRoom`      | BOOLEAN    | Accept any room? |
| `roomType`       | VARCHAR    | Optional room type filter |
| `isLocked`       | BOOLEAN    | Preference locked in? |
| `createdAt`      | TIMESTAMP  | — |

**Unique constraint:** `(userId, preferenceRank)` — one preference per priority slot per user

> During `select-room`, the chosen room is saved here as preferenceRank=1. All preferences are wiped when a session ends.

---

### 5.5 `CounsellingSession`

Tracks the state of a live allocation session.

| Column          | Type         | Description |
|-----------------|--------------|-------------|
| `id`            | SERIAL PK    | — |
| `sessionName`   | VARCHAR      | Admin-given name (unique) |
| `sessionStatus` | ENUM         | `not_started`, `active`, `paused`, `completed` |
| `currentRank`   | INTEGER      | Which rank is currently picking |
| `currentUserId` | FK → User    | The user currently picking |
| `turnStartTime` | TIMESTAMP    | When the current turn started |
| `turnDuration`  | INTEGER      | Seconds allowed per rank (default: 30) |
| `startedAt`     | TIMESTAMP    | When session was started |
| `pausedAt`      | TIMESTAMP    | When session was paused |
| `completedAt`   | TIMESTAMP    | When session ended |
| `createdAt`     | TIMESTAMP    | — |
| `updatedAt`     | TIMESTAMP    | Auto-updated by trigger |

**Only one session should be `active` at a time** (enforced in application logic).

---

### 5.6 `TurnQueue` & `ProcessingQueue`

These are legacy queue tables from the original architecture that still exist in the DB.

**TurnQueue** — sequential rank-based queue for 30-second turns:

| Column         | Type       | Description |
|----------------|------------|-------------|
| `id`           | SERIAL PK  | — |
| `userId`       | FK → User  | One entry per user (unique) |
| `rank`         | INTEGER    | Counselling rank (unique) |
| `status`       | ENUM       | `pending`, `active`, `completed`, `skipped`, `timed_out` |
| `turnStartTime`| TIMESTAMP  | — |
| `turnEndTime`  | TIMESTAMP  | — |
| `lockedAt`     | TIMESTAMP  | — |

**ProcessingQueue** — async background processing queue:

| Column           | Type       | Description |
|------------------|------------|-------------|
| `id`             | SERIAL PK  | — |
| `userId`         | FK → User  | — |
| `rank`           | INTEGER    | — |
| `queuePosition`  | INTEGER    | Position in queue |
| `status`         | ENUM       | `queued`, `processing`, `completed`, `failed` |
| `assignedRoomId` | INTEGER    | Result room ID |
| `failureReason`  | VARCHAR    | If failed |
| `lockedAt`       | TIMESTAMP  | — |
| `processedAt`    | TIMESTAMP  | — |

> ⚠️ These are mostly managed by `dbconfig/queue_management.py` but are **not actively driving** the current allocation flow (which uses `CounsellingSession` directly).

---

### 5.7 `Friendship`

Tracks friend relationships between students (for roommate coordination).

| Column      | Type       | Description |
|-------------|------------|-------------|
| `id`        | SERIAL PK  | — |
| `userId`    | FK → User  | The sender |
| `friendId`  | FK → User  | The receiver |
| `status`    | ENUM       | `pending`, `accepted`, `rejected` |
| `createdAt` | TIMESTAMP  | — |

**Unique constraint:** `(userId, friendId)` — one relationship per pair (directional)

---

## 6. Enum Types

| Enum            | Values |
|-----------------|--------|
| `Gender`        | `male`, `female` (+ `'other'` stored as varchar in practice) |
| `UserRole`      | `user`, `admin` |
| `FriendStatus`  | `pending`, `accepted`, `rejected` |
| `SessionStatus` | `not_started`, `active`, `paused`, `completed` |
| `TurnStatus`    | `pending`, `active`, `completed`, `skipped`, `timed_out` |
| `ProcessingStatus` | `queued`, `processing`, `completed`, `failed` |
| `SelectionStatus`  | `waiting`, `active`, `completed`, `skipped`, `timed_out` |
| `ApprovalStatus`   | `pending`, `approved`, `rejected`, `expired` (legacy) |

---

## 7. API Modules

### `api.py` — Core REST Endpoints

| Route Pattern                              | Method | Description |
|--------------------------------------------|--------|-------------|
| `/api/hostels`                             | GET    | All hostels with room stats |
| `/api/hostels/{name}`                      | GET    | Single hostel details |
| `/api/hostels/{name}/blocks`               | GET    | Blocks in a hostel |
| `/api/blocks`                              | GET    | All blocks (filterable) |
| `/api/blocks/{hostel}/{block}`             | GET    | Block details |
| `/api/blocks/{hostel}/{block}/floors`      | GET    | Floors in a block |
| `/api/floors`                              | GET    | All floors (filterable) |
| `/api/floors/{hostel}/{block}/{floor}`     | GET    | Floor details |
| `/api/rooms/available`                     | GET    | Available rooms (filterable by hostel/block/floor/AC/deluxe/apartment) |
| `/api/rooms/{id}`                          | GET    | Room by ID |
| `/api/session/current`                     | GET    | Active counselling session |
| `/api/session/{id}`                        | GET    | Session by ID |
| `/api/preferences/{user_id}`              | GET    | User's preferences |
| `/api/preferences`                         | POST   | Create preference |
| `/api/preferences/{id}`                    | PUT    | Update preference |
| `/api/preferences/{id}`                    | DELETE | Delete preference |
| `/api/preferences/lock`                    | POST   | Lock all preferences (auth required) |
| `/api/assignments/{user_id}`               | GET    | User's room assignment |
| `/api/assignments/room/{room_id}`          | GET    | All users in a room |
| `/api/queue/turn/{user_id}`                | GET    | User's position in turn queue |
| `/api/friends/{user_id}`                   | GET    | All friendships |
| `/api/friends/{user_id}/accepted`          | GET    | Accepted friends only |
| `/api/friends/{user_id}/requests`          | GET    | Pending requests |
| `/api/friends/request`                     | POST   | Send friend request (by ID) |
| `/api/friends/{id}/accept`                 | PUT    | Accept request |
| `/api/friends/{id}/reject`                 | PUT    | Reject request |
| `/api/friends/{id}`                        | DELETE | Remove friend |

### `allocation.py` — Allocation Router (`/api/allocation/*`)

| Route                              | Method | Auth  | Description |
|------------------------------------|--------|-------|-------------|
| `/session/current`                 | GET    | Any   | Current session state |
| `/session/start`                   | POST   | Admin | Start a new session + begin auto-advance |
| `/session/stop`                    | POST   | Admin | End session, clear all assignments |
| `/session/pause`                   | POST   | Admin | Pause session |
| `/session/resume`                  | POST   | Admin | Resume paused session |
| `/session/next-rank`               | POST   | Admin | Force advance to next rank |
| `/clear-all-allocations`           | POST   | Admin | Clear assignments without stopping session |
| `/select-room`                     | POST   | User  | Student picks a room during their turn |

### `firebase_auth.py` — Auth Router (`/api/auth/*`)

| Route                     | Method | Description |
|---------------------------|--------|-------------|
| `/firebase`               | POST   | Login / register via Firebase |
| `/me`                     | GET    | Get current user profile |
| `/me`                     | PATCH  | Update registrationNumber / displayName |
| `/user/{firebase_uid}`    | GET    | Get user by Firebase UID |

### `friend_requests.py` — Friends Router (`/api/*`)

| Route                                  | Method | Description |
|----------------------------------------|--------|-------------|
| `/users/verify/{registration_number}`  | GET    | Verify user exists |
| `/friends/request`                     | POST   | Send friend request by registration number |
| `/friends/request/{id}/accept`         | POST   | Accept request |
| `/friends/request/{id}/reject`         | POST   | Reject request |
| `/friends/requests/pending`            | GET    | Incoming pending requests |
| `/friends/requests`                    | GET    | All requests (sent + received) |
| `/friends`                             | GET    | Accepted friends list |

---

## 8. Database Indexes

| Table            | Index Column(s)                  | Purpose |
|------------------|----------------------------------|---------|
| `User`           | `rank`                           | Fast rank-based lookup during turns |
| `User`           | `role`                           | Fast admin filtering |
| `User`           | `allocatedRoomId` (partial)      | Find allocated users |
| `Rooms`          | `hostelName`                     | Filter by hostel |
| `Rooms`          | `blockName`                      | Filter by block |
| `Rooms`          | `availableSlots` (partial > 0)   | Fast available room lookup |
| `Rooms`          | `isLocked`, `lockExpiresAt`      | Lock management |
| `Rooms`          | `assignedUserId` (partial)       | Legacy assignment lookup |
| `RoomAssignments`| `roomId`                         | Who's in this room |
| `RoomAssignments`| `userId`                         | What room is this user in |
| `TurnQueue`      | `rank`, `status`                 | Queue ordering |
| `ProcessingQueue`| `queuePosition`, `status`, `userId` | Queue processing |

---

## 9. Migration History

| # | File | What Changed |
|---|------|-------------|
| 000 | `000_initial_schema.sql` | Created `User`, `Hostel`, `Block`, `Floor`, `Room`, `Preference`, `Friendship`, `CounsellingSession`, `TurnQueue`, `ProcessingQueue`, `RoomAssignment`, `RoommateApproval`, `RoomLock` |
| 001 | `001_add_counselling_system.sql` | Added `SelectionStatus`, `ApprovalStatus`, queue tables, lock tables; added columns to existing tables |
| 002 | `002_add_firebase_auth.sql` | Added `firebaseUid`, `displayName`, `photoUrl`, `lastLoginAt` to `User`; dropped `passwordHash` |
| 003 | `003_cleanup_user_table.sql` | Removed legacy fields from `User`; made `registrationNumber` optional |
| 004 | `004_add_user_role.sql` | Added `UserRole` enum + `role` column to `User` |
| 005 | `005_denormalize_to_rooms_table.sql` | **Big refactor**: created flat `Rooms` table with all hostel/block/floor info as columns; migrated data; dropped `Hostel`, `Block`, `Floor`, `Room`, `RoomLock`, `RoomAssignment`, `RoommateApproval` |
| 006 | `006_add_room_assignments_table.sql` | Re-added `RoomAssignments` table (plural) to support multiple students per room |
| 007 | `007_add_allocated_room_to_user.sql` | Added `allocatedRoomId` and `allocatedAt` to `User` as a fast-lookup denormalized copy |

---

## 10. Known Issues & TODOs

| Issue | Location | Severity |
|-------|----------|----------|
| Hardcoded DB credentials (`localhost`/`admin`/`admin123`) | `allocation.py` (line 14–20), `/api/approvals` endpoints in `api.py` | 🔴 High — breaks in production |
| `AllocationAutoAdvance` is a **in-memory singleton** — lost on server restart | `allocation.py` | 🟡 Medium — session will stall if server restarts mid-session |
| `RoommateApproval` endpoints commented out | `api.py` (lines 585–598) | 🟡 Medium — feature not available |
| `GET /api/approvals/{user_id}` still queries a `RoommateApproval` table that was dropped | `api.py` | 🔴 High — will error if called |
| `TurnQueue` / `ProcessingQueue` not used in the current allocation flow | `dbconfig/queue_management.py` | 🟢 Low — legacy dead code |
| CORS `"*"` wildcard enabled | `api.py` line 32 | 🟡 Medium — should be removed in production |
