# Room Counselling System - Complete Concept & Architecture

## 📋 Table of Contents
1. [Problem Statement](#problem-statement)
2. [Solution Overview](#solution-overview)
3. [System Architecture](#system-architecture)
4. [Core Concepts](#core-concepts)
5. [User Journey](#user-journey)
6. [Technical Implementation](#technical-implementation)
7. [Key Algorithms](#key-algorithms)
8. [Database Design](#database-design)
9. [API Architecture](#api-architecture)
10. [Real-time Features](#real-time-features)

---

## 🎯 Problem Statement

### The Challenge
In traditional hostel room allocation systems for colleges/universities:
- **Manual & Time-Consuming**: Admins manually assign rooms based on ranks/preferences
- **No Student Control**: Students can't choose roommates or see available rooms in real-time
- **Inefficient**: Sequential processing means low-ranked students wait hours/days
- **No Transparency**: Students don't know when their turn is or what rooms are available
- **Roommate Conflicts**: No formal system for roommate approval before assignment
- **Race Conditions**: Multiple admins might assign the same room to different students

### Requirements
1. **Fair rank-based system** - Higher rank gets priority
2. **Real-time room selection** - Students see and choose rooms during their turn
3. **Roommate approval system** - Friends must approve before being assigned together
4. **Time-bound turns** - Each student gets limited time to decide
5. **Parallel processing** - Multiple users processed simultaneously without blocking
6. **Admin control** - Pause/resume/monitor entire process
7. **Prevent conflicts** - Lock rooms during assignment to avoid double-booking

---

## 💡 Solution Overview

### The Big Idea: **Dual-Queue Architecture**

We separate the **decision-making** (Turn Queue) from the **execution** (Processing Queue):

```
┌─────────────────────────────────────────────────────────────┐
│                    COUNSELLING SESSION                       │
│  Status: Active | Current Rank: 15 | Turn Duration: 30s     │
└─────────────────────────────────────────────────────────────┘
                             │
                             ├──────────────────┐
                             ▼                  ▼
        ┌─────────────────────────┐  ┌──────────────────────────┐
        │   TURN QUEUE            │  │  PROCESSING QUEUE         │
        │   (Sequential)          │  │  (Parallel)               │
        ├─────────────────────────┤  ├──────────────────────────┤
        │ Rank 1: ✓ Completed     │  │ Processing: 5 users      │
        │ Rank 2: ✓ Completed     │  │ Queued: 12 users         │
        │ ...                     │  │ Completed: 2 users       │
        │ Rank 15: 🔵 Active      │  │ Failed: 0 users          │
        │          ⏱️ 18s left    │  │                          │
        │ Rank 16: ⏳ Pending     │  │ [User 15] → Processing   │
        │ Rank 17: ⏳ Pending     │  │ [User 12] → Processing   │
        │ ...                     │  │ [User 8]  → Processing   │
        └─────────────────────────┘  └──────────────────────────┘
```

### Key Innovation
- **Turn Queue moves immediately** when user locks preferences (doesn't wait for room assignment)
- **Processing Queue handles complex logic** (roommate approvals, preference matching, room locking) in background
- **Both queues run in parallel** - User 16's turn can start while User 15's preferences are still being processed

---

## 🏗️ System Architecture

### High-Level Components

```
┌──────────────────────────────────────────────────────────────┐
│                        FRONTEND                               │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐    │
│  │ Student  │  │ Admin    │  │ Real-time│  │ Dashboard│    │
│  │ Portal   │  │ Panel    │  │ Updates  │  │ Analytics│    │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘    │
└──────────────────────────────────────────────────────────────┘
                             │
                    WebSocket + REST API
                             │
┌──────────────────────────────────────────────────────────────┐
│                      BACKEND (Python)                         │
│  ┌─────────────────────────────────────────────────────┐    │
│  │              API Layer (Flask/FastAPI)               │    │
│  ├─────────────────────────────────────────────────────┤    │
│  │  Authentication │ Authorization │ Rate Limiting      │    │
│  └─────────────────────────────────────────────────────┘    │
│                             │                                 │
│  ┌─────────────────────────────────────────────────────┐    │
│  │           Business Logic Layer                       │    │
│  ├─────────────────────────────────────────────────────┤    │
│  │ • Session Manager    • Queue Controller             │    │
│  │ • Preference Engine  • Roommate Matcher             │    │
│  │ • Room Allocator     • Turn Timer                   │    │
│  │ • Lock Manager       • Notification Service         │    │
│  └─────────────────────────────────────────────────────┘    │
│                             │                                 │
│  ┌─────────────────────────────────────────────────────┐    │
│  │              Data Access Layer (CRUD)                │    │
│  ├─────────────────────────────────────────────────────┤    │
│  │ 12 CRUD Modules (psycopg2 + PostgreSQL)             │    │
│  └─────────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────────┘
                             │
┌──────────────────────────────────────────────────────────────┐
│                  DATABASE (PostgreSQL)                        │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐    │
│  │ Users &  │  │ Hostel   │  │ Session  │  │ Queues & │    │
│  │ Friends  │  │ Structure│  │ & Prefs  │  │ Approvals│    │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘    │
└──────────────────────────────────────────────────────────────┘
```

---

## 🔑 Core Concepts

### 1. **Rank-Based Priority System**
- Each student has a unique rank (1 to N)
- Lower rank number = Higher priority (Rank 1 goes first)
- Turns happen sequentially in rank order
- Cannot skip ahead in line

### 2. **30-Second Turn Timer**
- Each student gets exactly 30 seconds for their turn
- Timer starts when their rank becomes active
- User can lock preferences early (doesn't have to use full 30 seconds)
- If timer expires without locking, turn is marked as "timed_out"

### 3. **5 Preference System**
Each student can select up to 5 room preferences in priority order:

**Preference Types:**
- **Specific Room**: "I want Room 205 in Block A with my friends"
- **Any Room with Criteria**: "I want any AC room with 4-bed capacity"

**Preference Structure:**
```javascript
{
  rank: 1,  // Preference priority (1 = most preferred)
  roomId: 205 || null,  // Specific room OR null for "any"
  isAnyRoom: false,     // true if "any room matching criteria"
  roomType: "AC_4BED",  // Criteria when isAnyRoom = true
  roommateIds: [45, 67, 89],  // Friends I want as roommates
  isLocked: false       // true when submitted
}
```

### 4. **Roommate Approval System**

**Non-Exclusive Approvals:**
- User A can approve multiple people (B, C, D) as potential roommates
- Approvals are NOT binding commitments
- Just means "I'm okay rooming with you if we both end up in same room"

**Approval Flow:**
```
User A (Rank 10) wants User B (Rank 45) as roommate:
1. User A sends approval request to User B
2. User B receives notification
3. User B approves (or rejects) the request
4. Approval stored with status: 'approved'

Later, User A locks preferences:
5. Preference includes roomId=205, roommateIds=[B]
6. System checks: Is B approved? ✓ Yes
7. System checks: Is B already assigned? ✗ No
8. System checks: Will B fit in room? ✓ Yes (room has space)
9. SUCCESS: Both A and B assigned to Room 205
```

**Important Rules:**
- Approvals can be given BEFORE or DURING the session
- **Approval Expiration Logic:**
  - **Before Session Starts:** Approvals older than 24 hours expire automatically
  - **During Active Session:** Approvals do NOT expire based on time (session might take hours)
  - **After Assignment:** When someone gets assigned, ALL their pending approvals expire immediately
  - **Rationale:** A student might send approval requests hours before the session. Once the session starts, all approvals remain valid regardless of time, ensuring no mid-session expiration surprises
- Failed preference frees up roommates (they can be selected by others)
- **Group ID Linking:** All students assigned together through one preference share the same `groupId` in RoomAssignment table, forming a formal roommate group for tracking and reporting

### 5. **Room Lock Mechanism**

**Purpose:** Prevent race conditions during assignment

**How It Works:**
```
1. Processing starts for User A's preference (Room 205)
2. System creates RoomLock:
   - roomId: 205
   - lockedBy: User A
   - duration: 30 seconds
   - lockedAt: 2025-10-27 10:30:00

3. While locked, NO other user can be assigned to Room 205

4. Lock auto-expires after 30 seconds OR released manually

5. If assignment succeeds: Lock released, room occupancy updated
   If assignment fails: Lock released, room stays available
```

### 6. **Processing Engine Logic**

**Auto-Fallback System:**
When a user locks preferences, the system tries them in order:

```python
preferences = [Pref1, Pref2, Pref3, Pref4, Pref5]

for pref in preferences:
    result = try_assign_room(pref)
    
    if result.success:
        # Assign room, mark processing as completed
        assign_room(user, pref.roomId)
        mark_completed(user, assigned_room=pref.roomId)
        break
    else:
        # Log failure reason, try next preference
        log_failure(pref, result.reason)
        continue

# If all 5 preferences fail:
mark_failed(user, reason="All preferences unavailable")
```

**Failure Reasons:**
- Room already full
- Roommate not approved
- Roommate already assigned elsewhere
- Room locked by another user
- Preference no longer valid

### 7. **Dual Queue State Machine**

**Turn Queue States:**
```
pending → active → completed
                 ↘ skipped
                 ↘ timed_out
```

**Processing Queue States:**
```
queued → processing → completed
                    ↘ failed
```

**Synchronization Point:**
> Processing for rank N **MUST** complete before Turn Queue reaches rank N+1

**Implementation Details:**
The `advance_to_next_rank()` function enforces this synchronization through a pre-check:

```python
def advance_to_next_rank(session_id):
    session = get_session_by_id(session_id)
    current_rank = session['currentRank']
    
    # CRITICAL: Check if all processing for current rank is complete
    processing_entries = get_processing_by_rank(current_rank)
    
    for entry in processing_entries:
        if entry['status'] in ['queued', 'processing']:
            # Processing still ongoing, cannot advance
            return False
    
    # All processing complete (succeeded or failed), safe to advance
    update_current_rank(session_id, current_rank + 1)
    start_turn(current_rank + 1)
    return True
```

**Why This Matters:**
- Even if Rank 15 locks preferences in 5s and Rank 16's turn starts, Rank 15's processing might still be evaluating preferences 2-5
- Rank 16 can browse rooms and make selections during their 30s turn
- But when Rank 16 locks their preferences, the system won't process them until Rank 15's entry is marked `completed` or `failed`
- This prevents Rank 16 from "stealing" Room 205 while Rank 15's fallback preferences are still being evaluated

**Background Job Implementation:**
```python
def check_and_advance_turn():
    """Runs every 2 seconds to check for turn advancement"""
    session = get_active_session()
    current_turn = get_turn_by_rank(session['currentRank'])
    
    if current_turn['status'] == 'completed':
        # Turn ended, but check processing completion before advancing
        if can_advance_to_next_rank(session['id']):
            advance_to_next_rank(session['id'])
```

This ensures:
- Higher rank students get their choices processed first (strict ordering)
- Lower rank students see accurate room availability (no race conditions)
- No unfair advantage due to processing delays (synchronization enforced)

---

## 👥 User Journey

### **Student Journey**

#### Phase 1: Pre-Session (Before counselling starts)
```
1. Login to portal
2. View hostel structure (hostels → blocks → floors → rooms)
3. Send friend requests to potential roommates
4. Receive & approve roommate requests from others
5. Wait for session to start
```

#### Phase 2: Waiting for Turn
```
1. Session starts (Admin clicks "Start")
2. Student sees: "Your rank: 45 | Current rank: 1 | Estimated wait: 22 minutes"
3. Real-time updates via WebSocket:
   - "Rank 1 completed - assigned to Room 302"
   - "Rank 2 active - 25s remaining"
   - "Current rank: 15 | Estimated wait: 15 minutes"
4. Student can browse available rooms while waiting
```

#### Phase 3: Active Turn (30 seconds)
```
1. Notification: "Your turn has started! 30 seconds remaining"
2. Student sees:
   ┌────────────────────────────────────────┐
   │  YOUR TURN - 28 seconds remaining      │
   ├────────────────────────────────────────┤
   │  Preference 1: [Select Room ▼]         │
   │    ☐ Any AC room (4-bed)               │
   │    Roommates: [+Add] [User B] [User C] │
   │                                         │
   │  Preference 2: [Room 205 ▼]            │
   │    Roommates: [User B]                 │
   │                                         │
   │  Preference 3: ...                     │
   │                                         │
   │  [Lock Preferences & Submit]           │
   └────────────────────────────────────────┘
3. Timer counts down: 28... 27... 26...
4. Student selects 5 preferences with roommates
5. Clicks "Lock Preferences" (turn ends immediately)
```

#### Phase 4: Processing
```
1. "Preferences submitted! Processing..."
2. Student sees processing status:
   ┌────────────────────────────────────────┐
   │  PROCESSING YOUR PREFERENCES           │
   ├────────────────────────────────────────┤
   │  ✗ Preference 1: Room full             │
   │  ⏳ Preference 2: Checking availability │
   │  ⏸ Preference 3: Waiting...            │
   │  ⏸ Preference 4: Waiting...            │
   │  ⏸ Preference 5: Waiting...            │
   └────────────────────────────────────────┘
3. Real-time updates as each preference is tried
```

#### Phase 5: Assignment Result
```
SUCCESS:
┌────────────────────────────────────────┐
│  🎉 ROOM ASSIGNED!                     │
├────────────────────────────────────────┤
│  Room: 205, Floor 2, Block A           │
│  Hostel: Boys Hostel 1                 │
│  Roommates: User B, User C             │
│  Capacity: 4-bed (3/4 filled)          │
│                                         │
│  [View Room Details] [Download Pass]   │
└────────────────────────────────────────┘

FAILURE:
┌────────────────────────────────────────┐
│  ❌ NO ROOM ASSIGNED                   │
├────────────────────────────────────────┤
│  All your preferences were unavailable │
│  Reasons:                              │
│  • Preference 1: Room full             │
│  • Preference 2: Roommate unavailable  │
│  • Preference 3: Room already locked   │
│  • Preference 4: Room full             │
│  • Preference 5: Room full             │
│                                         │
│  Contact admin for manual assignment   │
└────────────────────────────────────────┘
```

### **Admin Journey**

#### Setup Phase
```
1. Import student list (CSV/Excel)
   - name, email, registration number, rank, gender
2. Setup hostel structure (if not exists)
   - Create hostels, blocks, floors, rooms
3. Create counselling session:
   - Max rank: 100
   - Turn duration: 30 seconds
   - Gender: Male/Female/Mixed
```

#### Active Session
```
1. Click "Start Session"
2. Monitor dashboard in real-time:
   ┌─────────────────────────────────────────────┐
   │  COUNSELLING SESSION DASHBOARD              │
   ├─────────────────────────────────────────────┤
   │  Status: ● Active                           │
   │  Current Rank: 23/100                       │
   │  Progress: ████████░░░░░░░░ 23%             │
   │  Elapsed: 11:30 | Estimated: 38:30          │
   │                                              │
   │  Turn Queue:                                │
   │  ✓ Completed: 20 | ⏱️ Active: 1             │
   │  ⏳ Pending: 79  | ⚠️ Timeout: 2            │
   │                                              │
   │  Processing Queue:                          │
   │  ⏳ Queued: 8   | 🔄 Processing: 5          │
   │  ✅ Success: 18 | ❌ Failed: 2              │
   │                                              │
   │  Rooms: 450 total | 432 available (96%)    │
   │                                              │
   │  [Pause] [Skip Current] [View Logs]        │
   └─────────────────────────────────────────────┘
3. Handle edge cases:
   - Pause if technical issue
   - Skip user if not responding
   - Manually assign if preferences fail
```

#### Completion Phase
```
1. All users processed
2. Click "Complete Session"
3. Generate reports:
   - Assignment list (CSV/PDF)
   - Statistics (success rate, avg time, etc.)
   - Unassigned students list
4. Export data for hostel records
```

---

## 🔧 Technical Implementation

### Technology Stack

**Backend:**
- **Language**: Python 3.12
- **Framework**: Flask or FastAPI
- **Database**: PostgreSQL 16.3
- **DB Library**: psycopg2-binary
- **Auth**: JWT (JSON Web Tokens)
- **Real-time**: WebSockets (SocketIO or WebSocket)
- **Password**: bcrypt

**Frontend (Suggested):**
- React.js or Next.js
- TailwindCSS for styling
- Socket.IO client for real-time
- React Query for API state management

**Infrastructure:**
- Docker for PostgreSQL
- **Redis for high-performance operations:**
  - **Turn Timer Cache:** Store `(userId, turnExpiryTimestamp)` for sub-second countdown checks
  - **Room Locks:** Use Redis SETNX/RedLock for ephemeral locks (faster than PostgreSQL, auto-expiry)
  - **Live Room Availability:** Cache available rooms list, invalidate on assignment (serves hundreds of students browsing simultaneously)
  - **Session State:** Cache active session data to reduce DB load during peak activity
- Nginx as reverse proxy

### Database Schema (13 Tables)

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                          DATABASE SCHEMA DIAGRAM                                     │
└─────────────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────┐
│         User             │
├──────────────────────────┤
│ • id (PK)               │
│ • name                  │
│ • email (unique)        │
│ • password (hashed)     │
│ • registrationNumber    │
│ • gender                │
│ • rank (unique)         │
│ • isActive              │
│ • createdAt             │
└──────────┬───────────────┘
           │
           ├─────────────────────────────────────┐
           │                                     │
           ▼                                     ▼
┌──────────────────────────┐         ┌──────────────────────────┐
│      Friendship          │         │      TurnQueue           │
├──────────────────────────┤         ├──────────────────────────┤
│ • id (PK)               │         │ • id (PK)               │
│ • user1Id (FK → User)   │         │ • userId (FK → User)    │
│ • user2Id (FK → User)   │         │ • rank                  │
│ • status (enum)         │         │ • status (enum)         │
│ • createdAt             │         │ • turnStartTime         │
│ • updatedAt             │         │ • turnEndTime           │
└──────────────────────────┘         │ • lockedAt              │
                                     │ • createdAt             │
                                     └──────────────────────────┘

┌──────────────────────────┐         ┌──────────────────────────┐
│   ProcessingQueue        │         │   RoommateApproval       │
├──────────────────────────┤         ├──────────────────────────┤
│ • id (PK)               │         │ • id (PK)               │
│ • userId (FK → User)    │         │ • requesterId (FK → User)│
│ • rank                  │         │ • approverId (FK → User) │
│ • queuePosition         │         │ • roomId (FK → Room)    │
│ • status (enum)         │         │ • status (enum)         │
│ • lockedAt              │         │ • requestedAt           │
│ • processedAt           │         │ • respondedAt           │
│ • assignedRoomId (FK)   │         │ • createdAt             │
│ • failureReason         │         └──────────────────────────┘
│ • createdAt             │
└──────────────────────────┘

┌──────────────────────────┐         ┌──────────────────────────┐
│   Preference             │         │   RoomAssignment         │
├──────────────────────────┤         ├──────────────────────────┤
│ • id (PK)               │         │ • id (PK)               │
│ • userId (FK → User)    │         │ • userId (FK → User)    │
│ • roomId (FK → Room)    │         │ • roomId (FK → Room)    │
│ • rank (1-5)            │         │ • groupId (UUID)        │
│ • isAnyRoom             │         │ • assignedAt            │
│ • roomType              │         │ • createdAt             │
│ • roommateIds (array)   │         └──────────┬───────────────┘
│ • isLocked              │                    │
│ • createdAt             │                    │
└──────────────────────────┘                    │
                                                │
┌──────────────────────────┐                    │
│  CounsellingSession      │                    │
├──────────────────────────┤                    │
│ • id (PK)               │                    │
│ • status (enum)         │                    │
│ • currentRank           │                    │
│ • maxRank               │                    │
│ • turnDuration (sec)    │                    │
│ • startedAt             │                    │
│ • pausedAt              │                    │
│ • completedAt           │                    │
│ • createdAt             │                    │
└──────────────────────────┘                    │
                                                │
                                                ▼
┌──────────────────────────┐         ┌──────────────────────────┐
│       Hostel             │         │        Room              │
├──────────────────────────┤         ├──────────────────────────┤
│ • id (PK)               │         │ • id (PK)               │
│ • name                  │◄────┐   │ • roomNumber            │
│ • gender                │     │   │ • floor                 │
│ • createdAt             │     │   │ • blockId (FK → Block)  │
└──────────────────────────┘     │   │ • capacity              │
                                 │   │ • currentOccupancy      │
┌──────────────────────────┐     │   │ • isAvailable           │
│        Block             │     │   │ • createdAt             │
├──────────────────────────┤     │   └──────────┬───────────────┘
│ • id (PK)               │     │              │
│ • name                  │     │              │
│ • hostelId (FK) ────────┼─────┘              │
│ • isAC                  │                    │
│ • createdAt             │                    │
└──────────┬───────────────┘                    │
           │                                    │
           ▼                                    │
┌──────────────────────────┐                    │
│        Floor             │                    │
├──────────────────────────┤                    │
│ • id (PK)               │                    │
│ • floorNumber           │                    │
│ • blockId (FK → Block)  │                    │
│ • createdAt             │                    │
└──────────────────────────┘                    │
                                                │
                                                ▼
                                     ┌──────────────────────────┐
                                     │      RoomLock            │
                                     ├──────────────────────────┤
                                     │ • id (PK)               │
                                     │ • roomId (FK → Room)    │
                                     │ • lockedByUserId (FK)   │
                                     │ • lockDuration (sec)    │
                                     │ • lockedAt              │
                                     │ • releasedAt            │
                                     │ • createdAt             │
                                     └──────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────────┐
│                              RELATIONSHIPS                                           │
├─────────────────────────────────────────────────────────────────────────────────────┤
│  User ──< Friendship (1:N) - user1Id, user2Id                                      │
│  User ──< TurnQueue (1:1) - One turn per user per session                          │
│  User ──< ProcessingQueue (1:N) - User can have multiple processing entries        │
│  User ──< Preference (1:N) - User has up to 5 preferences                          │
│  User ──< RoomAssignment (1:1) - User gets one room assignment                     │
│  User ──< RoommateApproval (1:N) - User can send/receive multiple approvals       │
│  Hostel ──< Block (1:N) - Hostel contains multiple blocks                          │
│  Block ──< Floor (1:N) - Block contains multiple floors                            │
│  Block ──< Room (1:N) - Block contains multiple rooms                              │
│  Room ──< Preference (1:N) - Room can be preferred by multiple users               │
│  Room ──< RoomAssignment (1:N) - Room can have multiple assignments (up to capacity)│
│  Room ──< RoomLock (1:N) - Room can have multiple lock entries (historical)        │
│  Room ──< RoommateApproval (N:1) - Optional room specification in approval         │
│  ProcessingQueue.assignedRoomId → Room - Links processing result to room           │
└─────────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────────┐
│                              ENUMS                                                   │
├─────────────────────────────────────────────────────────────────────────────────────┤
│  FriendshipStatus: pending, accepted, rejected                                      │
│  TurnStatus: pending, active, completed, skipped, timed_out                         │
│  ProcessingStatus: queued, processing, completed, failed                            │
│  ApprovalStatus: pending, approved, rejected, expired                               │
│  SessionStatus: not_started, active, paused, completed                              │
│  Gender: male, female, other                                                        │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

**Detailed Table Schemas:**

```sql
-- Core User Management
CREATE TABLE "User" (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,  -- bcrypt hashed
    "registrationNumber" VARCHAR(50) UNIQUE NOT NULL,
    gender VARCHAR(20) NOT NULL,
    rank INTEGER UNIQUE NOT NULL,
    "isActive" BOOLEAN DEFAULT true,
    "createdAt" TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE "Friendship" (
    id SERIAL PRIMARY KEY,
    "user1Id" INTEGER NOT NULL REFERENCES "User"(id) ON DELETE CASCADE,
    "user2Id" INTEGER NOT NULL REFERENCES "User"(id) ON DELETE CASCADE,
    status VARCHAR(20) DEFAULT 'pending',
    "createdAt" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT unique_friendship UNIQUE("user1Id", "user2Id")
);

-- Hostel Infrastructure
CREATE TABLE "Hostel" (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    gender VARCHAR(20) NOT NULL,
    "createdAt" TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE "Block" (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    "hostelId" INTEGER NOT NULL REFERENCES "Hostel"(id) ON DELETE CASCADE,
    "isAC" BOOLEAN DEFAULT false,
    "createdAt" TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE "Floor" (
    id SERIAL PRIMARY KEY,
    "floorNumber" INTEGER NOT NULL,
    "blockId" INTEGER NOT NULL REFERENCES "Block"(id) ON DELETE CASCADE,
    "createdAt" TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE "Room" (
    id SERIAL PRIMARY KEY,
    "roomNumber" VARCHAR(50) NOT NULL,
    floor INTEGER NOT NULL,
    "blockId" INTEGER NOT NULL REFERENCES "Block"(id) ON DELETE CASCADE,
    capacity INTEGER NOT NULL,
    "currentOccupancy" INTEGER DEFAULT 0,
    "isAvailable" BOOLEAN DEFAULT true,
    "createdAt" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT valid_occupancy CHECK ("currentOccupancy" <= capacity AND "currentOccupancy" >= 0)
);

-- Counselling System
CREATE TABLE "CounsellingSession" (
    id SERIAL PRIMARY KEY,
    status VARCHAR(20) DEFAULT 'not_started',
    "currentRank" INTEGER DEFAULT 1,
    "maxRank" INTEGER NOT NULL,
    "turnDuration" INTEGER DEFAULT 30,
    "startedAt" TIMESTAMP,
    "pausedAt" TIMESTAMP,
    "completedAt" TIMESTAMP,
    "createdAt" TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE "TurnQueue" (
    id SERIAL PRIMARY KEY,
    "userId" INTEGER UNIQUE NOT NULL REFERENCES "User"(id) ON DELETE CASCADE,
    rank INTEGER NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    "turnStartTime" TIMESTAMP,
    "turnEndTime" TIMESTAMP,
    "lockedAt" TIMESTAMP,
    "createdAt" TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE "ProcessingQueue" (
    id SERIAL PRIMARY KEY,
    "userId" INTEGER NOT NULL REFERENCES "User"(id) ON DELETE CASCADE,
    rank INTEGER NOT NULL,
    "queuePosition" INTEGER NOT NULL,
    status VARCHAR(20) DEFAULT 'queued',
    "lockedAt" TIMESTAMP,
    "processedAt" TIMESTAMP,
    "assignedRoomId" INTEGER REFERENCES "Room"(id),
    "failureReason" TEXT,
    "createdAt" TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Preferences & Assignments
CREATE TABLE "Preference" (
    id SERIAL PRIMARY KEY,
    "userId" INTEGER NOT NULL REFERENCES "User"(id) ON DELETE CASCADE,
    "roomId" INTEGER REFERENCES "Room"(id),
    rank INTEGER NOT NULL CHECK (rank >= 1 AND rank <= 5),
    "isAnyRoom" BOOLEAN DEFAULT false,
    "roomType" VARCHAR(50),
    "roommateIds" INTEGER[],
    "isLocked" BOOLEAN DEFAULT false,
    "createdAt" TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE "RoomAssignment" (
    id SERIAL PRIMARY KEY,
    "userId" INTEGER UNIQUE NOT NULL REFERENCES "User"(id) ON DELETE CASCADE,
    "roomId" INTEGER NOT NULL REFERENCES "Room"(id) ON DELETE CASCADE,
    "groupId" UUID,
    "assignedAt" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    "createdAt" TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Approval & Locking
CREATE TABLE "RoommateApproval" (
    id SERIAL PRIMARY KEY,
    "requesterId" INTEGER NOT NULL REFERENCES "User"(id) ON DELETE CASCADE,
    "approverId" INTEGER NOT NULL REFERENCES "User"(id) ON DELETE CASCADE,
    "roomId" INTEGER REFERENCES "Room"(id),
    status VARCHAR(20) DEFAULT 'pending',
    "requestedAt" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    "respondedAt" TIMESTAMP,
    CONSTRAINT no_self_approval CHECK ("requesterId" != "approverId")
);

CREATE TABLE "RoomLock" (
    id SERIAL PRIMARY KEY,
    "roomId" INTEGER NOT NULL REFERENCES "Room"(id) ON DELETE CASCADE,
    "lockedByUserId" INTEGER NOT NULL REFERENCES "User"(id) ON DELETE CASCADE,
    "lockDuration" INTEGER DEFAULT 30,
    "lockedAt" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    "releasedAt" TIMESTAMP,
    "createdAt" TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### CRUD Operations (100+ Functions)

We have 12 CRUD modules covering:
1. **user.py** - User authentication & management
2. **friendship.py** - Friend requests & relationships
3. **hostel.py** - Hostel CRUD
4. **block.py** - Block management
5. **floor.py** - Floor operations
6. **room.py** - Room availability & occupancy
7. **preference.py** - Preference submission & locking
8. **room_assignment.py** - Final room assignments
9. **counselling_session.py** - Session lifecycle management
10. **queue_management.py** - Turn & Processing queue operations
11. **roommate_approval.py** - Approval requests & responses
12. **room_lock.py** - Temporary room locks

---

## 🧮 Key Algorithms

### Algorithm 1: Turn Timer Management

```python
def check_and_advance_turn():
    """Background job that runs every 5 seconds"""
    session = get_active_session()
    if not session:
        return
    
    # Get current turn
    current_turn = get_turn_by_rank(session['currentRank'])
    
    if current_turn['status'] == 'active':
        # Check if turn expired
        if is_turn_expired(session['id']):
            # Timeout the turn
            timeout_turn(current_turn['rank'])
            
            # Advance to next rank
            advance_to_next_rank(session['id'])
            
            # Notify via WebSocket
            broadcast_event('turn_timeout', {
                'rank': current_turn['rank'],
                'userId': current_turn['userId']
            })
            broadcast_event('turn_started', {
                'rank': session['currentRank'] + 1
            })
    
    elif current_turn['status'] == 'completed':
        # Turn completed early, advance immediately
        advance_to_next_rank(session['id'])
```

### Algorithm 2: Preference Processing Engine

```python
def process_user_preferences(user_id, rank):
    """Process user's locked preferences"""
    
    # Get user's preferences (ordered by rank 1-5)
    preferences = get_preferences_by_user(user_id)
    
    for pref in preferences:
        try:
            # Step 1: Determine target room(s)
            if pref['isAnyRoom']:
                # Find any available room matching criteria
                rooms = find_rooms_by_criteria(pref['roomType'])
            else:
                # Specific room requested
                rooms = [get_room_by_id(pref['roomId'])]
            
            # Step 2: Try each matching room
            for room in rooms:
                # Check if room is available
                if not room['isAvailable'] or room['currentOccupancy'] >= room['capacity']:
                    continue
                
                # Check if room is locked
                if is_room_locked(room['id']):
                    continue
                
                # Step 3: Lock the room (SHORT DURATION)
                # Lock only for actual processing time, not full 30s turn duration
                lock = create_room_lock(room['id'], user_id, duration=5)  # 5s processing lock
                
                try:
                    # Step 4: Validate roommates
                    roommates = []
                    if pref['roommateIds']:
                        for roommate_id in pref['roommateIds']:
                            # Check approval
                            if not check_approval_status(user_id, roommate_id):
                                raise Exception(f"Roommate {roommate_id} hasn't approved")
                            
                            # Check if roommate already assigned
                            if get_assignment_by_user(roommate_id):
                                raise Exception(f"Roommate {roommate_id} already assigned")
                            
                            roommates.append(roommate_id)
                    
                    # Step 5: Check capacity
                    total_students = 1 + len(roommates)
                    remaining_capacity = room['capacity'] - room['currentOccupancy']
                    
                    if total_students > remaining_capacity:
                        raise Exception("Room doesn't have enough capacity")
                    
                    # Step 6: Create assignments
                    group_id = generate_group_id()
                    
                    # Assign main user
                    create_assignment(user_id, room['id'], group_id)
                    increment_occupancy(room['id'])
                    
                    # Assign roommates
                    for roommate_id in roommates:
                        create_assignment(roommate_id, room['id'], group_id)
                        increment_occupancy(room['id'])
                        
                        # Expire their approvals
                        bulk_expire_requests_for_user(roommate_id)
                        
                        # Mark their turn as completed
                        complete_turn_by_user(roommate_id)
                    
                    # Step 7: Release lock & mark success
                    release_lock(lock['id'])
                    complete_processing(entry_id, assigned_room_id=room['id'])
                    
                    # Notify users
                    notify_assignment_success(user_id, roommates, room)
                    
                    return True  # Success!
                    
                except Exception as e:
                    # Release lock on failure
                    release_lock(lock['id'])
                    log_failure(pref, str(e))
                    continue  # Try next room
        
        except Exception as e:
            log_failure(pref, str(e))
            continue  # Try next preference
    
    # All preferences failed
    fail_processing(entry_id, failure_reason="All preferences unavailable")
    notify_assignment_failure(user_id)
    return False
```

### Algorithm 3: Room Availability Calculator

```python
def get_available_rooms_with_filters(filters):
    """Get available rooms based on complex filters"""
    
    query = """
        SELECT r.*, 
               (r.capacity - r."currentOccupancy") as "remainingCapacity",
               b.name as "blockName",
               b."isAC",
               h.name as "hostelName"
        FROM "Room" r
        JOIN "Block" b ON r."blockId" = b.id
        JOIN "Hostel" h ON b."hostelId" = h.id
        WHERE r."isAvailable" = true
          AND r."currentOccupancy" < r.capacity
    """
    
    params = []
    
    # Filter by hostel
    if filters.get('hostelId'):
        query += " AND h.id = %s"
        params.append(filters['hostelId'])
    
    # Filter by AC/Non-AC
    if filters.get('isAC') is not None:
        query += " AND b.\"isAC\" = %s"
        params.append(filters['isAC'])
    
    # Filter by capacity
    if filters.get('minCapacity'):
        query += " AND r.capacity >= %s"
        params.append(filters['minCapacity'])
    
    if filters.get('maxCapacity'):
        query += " AND r.capacity <= %s"
        params.append(filters['maxCapacity'])
    
    # Filter by required remaining space
    if filters.get('requiredSpace'):
        query += " AND (r.capacity - r.\"currentOccupancy\") >= %s"
        params.append(filters['requiredSpace'])
    
    # Check if room is locked
    query += """
        AND NOT EXISTS (
            SELECT 1 FROM "RoomLock" rl
            WHERE rl."roomId" = r.id
              AND rl."releasedAt" IS NULL
              AND rl."lockedAt" + (rl."lockDuration" || ' seconds')::INTERVAL > CURRENT_TIMESTAMP
        )
    """
    
    # CRITICAL: Secondary sort order for "Any Room" preferences
    # This ensures fair, consistent room allocation when multiple rooms match criteria
    query += """
        ORDER BY 
            r."currentOccupancy" DESC,  -- Fill rooms to capacity first (optimize space usage)
            r.floor ASC,                 -- Prefer lower floors (easier access)
            r."roomNumber" ASC           -- Consistent ordering for equal priority
    """
    
    return execute_query(query, params)
```

**Why This Ordering Matters:**
When a high-ranked student (Rank 1) selects "Any AC 4-bed room" and 10 rooms match:
- Without ordering: They might get randomly assigned Room 401 (empty) while Room 205 has 3 students waiting for a 4th
- With ordering: They get assigned to Room 205 (3/4 occupied), optimizing space and potentially creating complete room groups
- Lower floors are preferred as institutional policy (easier access, less stairs)
- Consistent roomNumber ordering ensures reproducible results for testing/debugging

---

## 📊 Database Design Highlights

### Indexes for Performance
```sql
-- User lookups
CREATE INDEX idx_user_email ON "User"(email);
CREATE INDEX idx_user_registration ON "User"("registrationNumber");
CREATE INDEX idx_user_rank ON "User"(rank);

-- Queue operations
CREATE INDEX idx_turn_queue_rank ON "TurnQueue"(rank);
CREATE INDEX idx_turn_queue_status ON "TurnQueue"(status);
CREATE INDEX idx_processing_queue_status ON "ProcessingQueue"(status);
CREATE INDEX idx_processing_queue_position ON "ProcessingQueue"("queuePosition");

-- Room availability
CREATE INDEX idx_room_available ON "Room"("isAvailable");
CREATE INDEX idx_room_block ON "Room"("blockId");

-- Approval lookups
CREATE INDEX idx_approval_approver ON "RoommateApproval"("approverId");
CREATE INDEX idx_approval_status ON "RoommateApproval"(status);

-- Lock checks
CREATE INDEX idx_room_lock_room ON "RoomLock"("roomId");
```

### Triggers & Constraints
```sql
-- Auto-update room availability when capacity reached
CREATE OR REPLACE FUNCTION update_room_availability()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW."currentOccupancy" >= NEW.capacity THEN
        NEW."isAvailable" = false;
    ELSE
        NEW."isAvailable" = true;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER room_availability_trigger
BEFORE UPDATE ON "Room"
FOR EACH ROW
EXECUTE FUNCTION update_room_availability();

-- Ensure unique ranks
ALTER TABLE "User" ADD CONSTRAINT unique_rank UNIQUE(rank);

-- Ensure valid capacity
ALTER TABLE "Room" ADD CONSTRAINT valid_occupancy 
CHECK ("currentOccupancy" <= capacity AND "currentOccupancy" >= 0);
```

---

## 🌐 API Architecture

### REST Endpoints (40+ endpoints)

**Authentication & Users:**
- `POST /api/auth/register`
- `POST /api/auth/login`
- `GET /api/auth/me`

**Session Management:**
- `POST /api/admin/sessions` - Create session
- `GET /api/session/current` - Get active session
- `PUT /api/admin/sessions/:id/start` - Start session
- `GET /api/session/my-turn` - Get my turn status

**Preferences:**
- `GET /api/preferences/my`
- `POST /api/preferences`
- `PUT /api/preferences/lock`

**Roommate Approvals:**
- `GET /api/roommates/pending`
- `POST /api/roommates/request`
- `PUT /api/roommates/:id/approve`

**Room Browsing:**
- `GET /api/rooms/available`
- `GET /api/rooms/:id`

**Admin Dashboard:**
- `GET /api/admin/dashboard`
- `GET /api/admin/analytics/session`
- `GET /api/admin/export/assignments`

### WebSocket Events (Real-time)

```javascript
// Client subscribes to events
socket.on('turn_started', (data) => {
  // { rank: 23, userId: 45, startTime, endTime }
  updateUI(data);
});

socket.on('turn_completed', (data) => {
  // { rank: 22, userId: 44, assignedRoom: 205 }
  showNotification(data);
});

socket.on('room_assigned', (data) => {
  // { userId: 45, roomId: 205, roommates: [67, 89] }
  if (data.userId === currentUser.id) {
    showSuccessModal(data);
  }
});

socket.on('approval_received', (data) => {
  // { requestId: 12, approverId: 67, approverName: "John" }
  showApprovalNotification(data);
});
```

---

## ⚡ Real-time Features

### 1. Live Turn Updates
Every 5 seconds, server broadcasts:
- Current active rank
- Time remaining for active turn
- Progress percentage

### 2. Room Availability Changes
When a room gets assigned:
- Update available room count
- Remove room from available list for all users
- Update hostel/block statistics

### 3. Processing Status
User sees real-time updates:
- "Checking preference 1..."
- "Preference 1 failed - Room full"
- "Trying preference 2..."
- "Success! Room 205 assigned"

### 4. Approval Notifications
Instant notifications when:
- Someone sends you a roommate request
- Someone approves your request
- Your roommate gets assigned (so you know they're no longer available)

---

## 🎯 Key Success Metrics

### Performance Targets
- **Turn advancement**: < 1 second after lock/timeout
- **Room assignment**: < 5 seconds average processing time
- **WebSocket latency**: < 200ms for event delivery
- **Database queries**: < 100ms for most operations
- **Concurrent users**: Support 500+ simultaneous connections

### Business Metrics
- **Success rate**: % of users who get assigned a room
- **Preference hit rate**: % of users who get their 1st preference
- **Average processing time**: Time from lock to assignment
- **Timeout rate**: % of users who don't respond in 30 seconds
- **System uptime**: 99.9% during active session

---

## 🔒 Security Considerations

### Authentication
- JWT tokens with 24-hour expiry
- Refresh token mechanism
- Password hashing with bcrypt (10 rounds)

### Authorization
- Role-based access control (Student vs Admin)
- Users can only access their own data
- Admin endpoints require admin role

### Rate Limiting
- 100 requests/minute for general API
- 1 lock request per 30 seconds
- WebSocket connection limits

### Data Validation
- Input sanitization for all user inputs
- SQL injection prevention (parameterized queries)
- XSS protection on frontend

---

## � Technical Refinements & Edge Case Handling

### 1. Dual-Queue Synchronization: Preventing Deadlocks

**The Challenge:**
If Rank 15 locks preferences in 5 seconds (turn ends early), Rank 16's turn immediately starts. But Rank 15's processing might take 20 seconds to try all 5 preferences. If Rank 16 also wants Room 205 and locks preferences in 10 seconds, we risk a race condition.

**The Solution: Strict Rank-Order Processing Completion**

The `advance_to_next_rank()` function implements a **two-phase check**:

```python
def can_advance_to_next_rank(session_id):
    """Check if it's safe to advance to next rank"""
    session = get_session_by_id(session_id)
    current_rank = session['currentRank']
    
    # Phase 1: Check if current turn is completed/timed_out
    current_turn = get_turn_by_rank(current_rank)
    if current_turn['status'] not in ['completed', 'timed_out', 'skipped']:
        return False  # Turn still active
    
    # Phase 2: CRITICAL - Check processing completion
    processing_entries = get_processing_entries_by_rank(current_rank)
    
    for entry in processing_entries:
        if entry['status'] in ['queued', 'processing']:
            # Still processing this rank's preferences
            return False
    
    # All processing complete (success or failure), safe to advance
    return True

def advance_to_next_rank(session_id):
    """Advance turn queue only if processing complete"""
    if not can_advance_to_next_rank(session_id):
        return False
    
    session = get_session_by_id(session_id)
    new_rank = session['currentRank'] + 1
    
    update_current_rank(session_id, new_rank)
    start_turn(new_rank)
    
    broadcast_event('turn_started', {
        'rank': new_rank,
        'timestamp': datetime.now()
    })
    
    return True
```

**How This Prevents Race Conditions:**

| Time | Rank 15 | Rank 16 | System State |
|------|---------|---------|--------------|
| T+0s | Turn starts | Waiting | currentRank = 15 |
| T+5s | Locks prefs (turn ends) | Waiting | Turn Queue: 15→completed, Processing: 15→queued |
| T+6s | Processing starts (Room 205) | Turn starts! | currentRank = 15 (NOT advanced yet) |
| T+16s | Pref 1 fails, trying Pref 2 | Browsing rooms | Processing: 15→processing |
| T+25s | Pref 2 succeeds (Room 301) | Locks prefs | Turn Queue: 16→completed, Processing: 16→queued |
| T+26s | Processing complete | **Queued (blocked)** | currentRank = 15 still |
| T+27s | Release locks, mark done | **Still queued** | Processing: 15→completed |
| T+28s | - | **Processing starts NOW** | currentRank = 16 (finally advanced) |

**Key Insight:** Rank 16 can browse, select, and lock preferences during their turn, but their processing **waits in queue** until Rank 15's processing is fully complete. This maintains strict rank ordering for room assignments.

### 2. Roommate Approval Expiration: Session-Aware Logic

**The Problem:**
Fixed 24-hour expiration could cause mid-session failures. A student sends approval at 8 AM, session starts at 2 PM (6 hours later), their turn comes at 6 PM (10 hours total), but the approval expires at 8 AM next day (still within session).

**The Solution: State-Based Expiration**

```python
def expire_old_pending_requests(session_aware=True):
    """Expire requests based on session state"""
    
    if session_aware:
        active_session = get_active_session()
        
        if active_session:
            # Session is running - DO NOT expire any approvals
            return 0
        else:
            # No active session - expire old requests (24h)
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE "RoommateApproval"
                SET status = 'expired',
                    "respondedAt" = CURRENT_TIMESTAMP
                WHERE status = 'pending'
                    AND "requestedAt" < CURRENT_TIMESTAMP - INTERVAL '24 hours'
                """
            )
            count = cursor.rowcount
            conn.commit()
            return count
    else:
        # Force expiration regardless of session (admin override)
        # ... existing logic
```

**Expiration Rules:**
1. **Pre-Session:** Approvals older than 24 hours expire automatically (cleanup old requests)
2. **During Session:** NO time-based expiration (session might take 2-3 hours for 500 students)
3. **Post-Assignment:** ALL approvals for assigned students expire immediately (frees them for others)
4. **Failed Preference:** Approvals remain valid (student can be selected by next ranker)

**Background Job:**
```python
def scheduled_approval_cleanup():
    """Runs every 1 hour"""
    expire_old_pending_requests(session_aware=True)
```

### 3. Room Lock Duration: Minimal Blocking

**The Problem:**
Original design: 30-second lock duration (matching turn timer). But if processing takes 2 seconds, the room stays locked for 28 unnecessary seconds, blocking lower-ranked students from viewing accurate availability.

**The Solution: Short, Precise Locks**

```python
# Recommended lock durations by operation type
LOCK_DURATIONS = {
    'assignment': 5,      # Actual room assignment (DB transactions)
    'validation': 3,      # Quick checks (approval, capacity)
    'emergency': 10       # Admin manual intervention
}

def create_room_lock(room_id, locked_by_user_id, lock_type='assignment'):
    """Create short-duration locks based on operation type"""
    duration = LOCK_DURATIONS.get(lock_type, 5)
    
    # For production: Use Redis for better performance
    # redis_client.setex(f'room_lock:{room_id}', duration, locked_by_user_id)
    
    # For now: PostgreSQL implementation
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute(
        """
        INSERT INTO "RoomLock" ("roomId", "lockedByUserId", "lockDuration")
        VALUES (%s, %s, %s)
        RETURNING *
        """,
        (room_id, locked_by_user_id, duration)
    )
    lock = dict(cursor.fetchone())
    conn.commit()
    return lock
```

**Lock Lifecycle:**
```python
# In processing algorithm:
lock = create_room_lock(room['id'], user_id, lock_type='assignment')  # 5s lock

try:
    # Fast operations: validate roommates, check capacity (< 1s)
    validate_roommates(pref['roommateIds'])
    check_capacity(room, total_students)
    
    # Assignment (< 2s): atomic transaction
    assign_room_with_roommates(user_id, room['id'], roommates)
    
    # Immediately release lock on success
    release_lock(lock['id'])
    
except Exception as e:
    # Immediately release lock on failure
    release_lock(lock['id'])
    raise e
```

**Benefits:**
- Room availability is more accurate for waiting students
- Reduced lock contention (more parallel processing possible)
- Automatic cleanup via auto-expiry (if release fails, 5s timeout)

### 4. Redis Integration: High-Performance Operations

**Architecture: Hybrid PostgreSQL + Redis**

```
┌─────────────────────────────────────────────────────────┐
│                    REDIS (In-Memory)                     │
├─────────────────────────────────────────────────────────┤
│  • Turn Timers: userId → expiryTimestamp                │
│  • Room Locks: roomId → (userId, expiryTime)            │
│  • Available Rooms Cache: List of available room IDs    │
│  • Session State: Current rank, status, startTime       │
└─────────────────────────────────────────────────────────┘
                            ↕ (Write-through cache)
┌─────────────────────────────────────────────────────────┐
│              POSTGRESQL (Persistent Storage)             │
├─────────────────────────────────────────────────────────┤
│  • All tables (source of truth)                         │
│  • Complex queries (joins, aggregations)                │
│  • Historical data & audit logs                         │
└─────────────────────────────────────────────────────────┘
```

**Implementation Examples:**

**A. Turn Timer (Redis-based):**
```python
import redis
redis_client = redis.Redis(host='localhost', port=6379, db=0)

def start_turn_with_redis(rank):
    """Start turn with Redis-backed timer"""
    turn = start_turn(rank)  # Update PostgreSQL
    
    # Store timer in Redis (faster checks)
    expiry_time = time.time() + 30  # 30 seconds from now
    redis_client.setex(
        f'turn_timer:{turn["userId"]}',
        30,  # TTL: 30 seconds
        expiry_time
    )
    
    return turn

def is_turn_expired_redis(user_id):
    """Check turn expiry from Redis (microsecond response time)"""
    expiry_time = redis_client.get(f'turn_timer:{user_id}')
    
    if not expiry_time:
        return True  # No timer found, assume expired
    
    return time.time() > float(expiry_time)
```

**B. Room Locks (Redis RedLock):**
```python
from redlock import Redlock

dlm = Redlock([{"host": "localhost", "port": 6379, "db": 0}])

def acquire_room_lock_redis(room_id, user_id, duration=5):
    """Acquire distributed lock using Redis"""
    lock_key = f'room_lock:{room_id}'
    lock_value = f'{user_id}:{time.time()}'
    
    # Try to acquire lock with 5-second TTL
    lock = dlm.lock(lock_key, duration * 1000)  # milliseconds
    
    if lock:
        return {
            'lockId': lock_key,
            'roomId': room_id,
            'userId': user_id,
            'expiresAt': time.time() + duration
        }
    else:
        return None  # Lock failed (room already locked)

def release_room_lock_redis(lock_key):
    """Release Redis lock"""
    dlm.unlock(lock_key)
```

**C. Available Rooms Cache:**
```python
def get_available_rooms_cached(filters):
    """Get available rooms with Redis caching"""
    cache_key = f'available_rooms:{hash(str(filters))}'
    
    # Try Redis first
    cached = redis_client.get(cache_key)
    if cached:
        return json.loads(cached)
    
    # Cache miss: Query PostgreSQL
    rooms = get_available_rooms_with_filters(filters)
    
    # Store in Redis with 10-second TTL
    redis_client.setex(cache_key, 10, json.dumps(rooms))
    
    return rooms

def invalidate_room_cache():
    """Clear room cache when assignment happens"""
    # Delete all keys matching pattern
    for key in redis_client.scan_iter('available_rooms:*'):
        redis_client.delete(key)
```

**Performance Comparison:**

| Operation | PostgreSQL | Redis | Speedup |
|-----------|-----------|-------|---------|
| Check turn expiry | 15-20ms | 0.5ms | **30-40x** |
| Acquire room lock | 10-15ms | 0.3ms | **30-50x** |
| Get available rooms | 50-100ms | 1-2ms | **50-100x** |
| Session state read | 8-12ms | 0.4ms | **20-30x** |

**Consistency Strategy:**
- Redis is **cache layer** (fast reads)
- PostgreSQL is **source of truth** (persistent writes)
- Write-through: Update both Redis + PostgreSQL on critical operations
- On Redis failure: Fall back to PostgreSQL (degraded performance, but still functional)

### 5. Group ID: Formal Roommate Linking

**Purpose:** Track which students were assigned together as roommates in a single transaction.

**Schema:**
```sql
RoomAssignment (
    id SERIAL PRIMARY KEY,
    userId INTEGER REFERENCES "User"(id),
    roomId INTEGER REFERENCES "Room"(id),
    groupId UUID,  -- Links all roommates assigned together
    assignedAt TIMESTAMP,
    createdAt TIMESTAMP
)
```

**Example:**
User A (Rank 10) locks preferences with roommates B, C. Preference 2 succeeds (Room 205):

```python
group_id = uuid.uuid4()  # Generate unique group ID

# Assign main user
create_assignment(user_a_id, room_205, group_id)  # groupId: 'abc-123'

# Assign roommates
create_assignment(user_b_id, room_205, group_id)  # groupId: 'abc-123' (SAME)
create_assignment(user_c_id, room_205, group_id)  # groupId: 'abc-123' (SAME)
```

**Query Examples:**
```sql
-- Get all roommates assigned with User A
SELECT u.name, u.registrationNumber
FROM "RoomAssignment" ra
JOIN "User" u ON ra."userId" = u.id
WHERE ra."groupId" = (
    SELECT "groupId" FROM "RoomAssignment" WHERE "userId" = <user_a_id>
);

-- Get assignment statistics by group size
SELECT 
    COUNT(DISTINCT "groupId") as total_groups,
    COUNT(*) / COUNT(DISTINCT "groupId") as avg_group_size
FROM "RoomAssignment";
```

**Benefits:**
- Clear audit trail (who was assigned with whom)
- Easy roommate lookups for admin dashboard
- Supports group-based operations (e.g., room swaps)
- Statistics tracking (how many students got roommates vs. solo assignments)

---

## �🚀 Deployment Strategy

### Development Environment
```
1. PostgreSQL in Docker
2. Python backend (Flask dev server)
3. React dev server with hot reload
4. Local Redis for caching
```

### Production Environment
```
1. PostgreSQL (AWS RDS or self-hosted)
2. Python backend (Gunicorn + 4 workers)
3. Nginx reverse proxy
4. Redis cluster
5. SSL/TLS certificates (Let's Encrypt)
6. Docker containers orchestrated with Docker Compose
```

### Monitoring & Logging
- Application logs (Winston/Python logging)
- Database query monitoring
- Real-time dashboard for admins
- Error tracking (Sentry)
- Performance monitoring (New Relic/DataDog)

---

## 📈 Future Enhancements

### Phase 2 Features
1. **Mobile App** - Native iOS/Android apps
2. **Room Swapping** - Post-assignment room exchanges
3. **Waitlist System** - Auto-assign when rooms become available
4. **AI Recommendations** - Suggest rooms based on preferences & friend groups
5. **Virtual Room Tours** - 360° photos of rooms
6. **Block Preferences** - Prefer entire blocks (close to friends)
7. **Multi-session Support** - Run multiple sessions for different groups
8. **Advanced Analytics** - Predict room demand, optimize turn order

### Scalability Improvements
1. **Microservices Architecture** - Separate services for queues, processing, notifications
2. **Message Queue** - RabbitMQ/Kafka for async processing
3. **Load Balancing** - Multiple backend instances
4. **Database Sharding** - Split data by hostel/gender
5. **CDN** - Static asset delivery
6. **Caching Layer** - Redis for hot data

---

## 🎓 Conclusion

This Room Counselling System solves the complex problem of fair, transparent, and efficient hostel room allocation through:

✅ **Rank-based fairness** - Priority queue ensures order  
✅ **Real-time transparency** - Students see exactly what's happening  
✅ **Parallel efficiency** - Dual queue system maximizes throughput  
✅ **Social features** - Roommate approval system reduces conflicts  
✅ **Technical robustness** - Locks prevent race conditions  
✅ **Admin control** - Pause/resume/monitor entire process  
✅ **Scalable architecture** - Handles 500+ users concurrently  

The system transforms what used to take days of manual work into a smooth, automated process that completes in 1-2 hours while giving students the power to choose their rooms and roommates!

---

**Built with:** Python 3.12 • PostgreSQL 16 • psycopg2 • JWT • WebSockets  
**Architecture:** Dual-Queue System with Real-time Processing  
**Status:** ✅ Database & CRUD layer complete | 🔄 API layer in progress

