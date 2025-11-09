# Hostel Counselling Backend# Hostel Counselling Backend



A FastAPI backend for hostel room counselling/allocation system with Firebase authentication.A FastAPI backend that implements a hostel room counselling/allocation system with Firebase authentication and a denormalized `Rooms` table. It supports a timed counselling session where users pick rooms in rank order, preference tracking, room locking, and admin operations.



## Deployment on RenderThis README explains the project architecture, how to set it up locally on Windows, database migrations, important endpoints (including admin endpoints), how allocation works, testing, and frontend compatibility notes.



### Environment Variables---



Set the following environment variables in Render:## Table of Contents



```- Project overview

DB_HOST=<your-postgres-host>- Key concepts and data model

DB_PORT=5432- Repo layout

DB_NAME=room_counselling- Requirements

DB_USER=<your-db-user>- Local setup (Windows PowerShell)

DB_PASSWORD=<your-db-password>- Database & migrations

```- Running the API server

- Important endpoints (quick reference)

### Build Command- Allocation workflow

- Admin operations (clear allocations, stop session, etc.)

```bash- Frontend changes and compatibility

pip install -r requirements.txt- Tests

```- Troubleshooting



### Start Command---



```bash## Project overview

uvicorn api:app --host 0.0.0.0 --port $PORT

```This service implements a hostel room allocation/counselling system where:



### Database Setup- Users are given ranks and have a limited time per rank to choose a room.

- Preferences are recorded (and can be migrated/updated).

1. Create a PostgreSQL database on Render- Rooms are stored in a denormalized `Rooms` table for fast lookups.

2. Run migrations in order from the `migrations/` folder- Room assignments are tracked in a `RoomAssignments` table (one row per user-room assignment).

3. Ensure Firebase service account key is properly configured- Rooms can be locked for a user while they decide.

- Admins can start/pause/stop sessions and clear allocations.

### Important Files- Firebase is used for authentication and role-based access (admin/user).



- `api.py` - Main FastAPI application---

- `allocation.py` - Allocation session logic

- `firebase_auth.py` - Firebase authentication## Key concepts and data model

- `dbconfig/` - Database configuration and models

- `migrations/` - SQL migration filesImportant tables (denormalized):

- `requirements.txt` - Python dependencies

- `Dockerfile` - Docker configuration- `Rooms` - denormalized table containing room metadata and occupancy (`capacity`, `occupied`).

- `RoomAssignments` - new table (migration 006) that stores one row per assignment: (`roomId`, `userId`, `assignedAt`).

### Notes- `Preference` - tracks user preference selections per session.

- `User` - user records (including `rank`, `role`, etc.).

- **IMPORTANT**: Do not commit `serviceAccountKey.json` to public repositories- `CounsellingSession` - session control (active/completed, current rank, timing).

- Update database credentials before deployment

- Use HTTPS in productionNotes:

- Configure CORS origins appropriately- `Rooms.assignedUserId` exists for backward compatibility but is deprecated. Use `RoomAssignments`.

- Price/fee fields (`rentPerSemester`, `pricePerSemester`) have been removed by request.

---

## Repo layout (important files)

- `api.py` - Main FastAPI app and many endpoints
- `allocation.py` - Allocation session endpoints and logic
- `dbconfig/room.py` - DB helpers for rooms and assignment operations
- `migrations/` - SQL migration files (see 005, 006)
- `apply_migration_006.py` - convenience script to apply migration 006
- `run_tests.py`, `run_expanded_tests.py` - included test scripts
- `FRONTEND_CHANGES_REQUIRED.md` - guidance for frontend updates after API changes
- `requirements.txt` - Python package requirements
- `serviceAccountKey.json` - Firebase credentials (sensitive - DO NOT commit publicly)

---

## Requirements

- Python 3.10+ (project used 3.12 in dev environment)
- PostgreSQL (local or remote)
- pip packages in `requirements.txt`
- Firebase project configuration for authentication

---

## Local setup (Windows PowerShell)

1. Create or activate a Python environment and install dependencies:

```powershell
# Using pyenv/venv as appropriate. Example:
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

2. Configure database connection in `dbconfig/room.py` or `allocation.py` if using different DB settings. Default DB_CONFIG in code is:

```python
DB_CONFIG = {
  'host': 'localhost',
  'port': 5432,
  'database': 'room_counselling',
  'user': 'admin',
  'password': 'admin123'
}
```

Change credentials before deploying to production.

3. Ensure PostgreSQL is running. On Windows you may need to start the service:

```powershell
# Run as Administrator if needed
Start-Service postgresql-x64-17
```

---

## Database & migrations

This repo stores schema changes as SQL in `migrations/`.

Key migration: `migrations/006_add_room_assignments_table.sql` - creates the `RoomAssignments` table and migrates existing assignments.

To apply migration 006 (convenience script included):

```powershell
python apply_migration_006.py
```

Or run directly with `psql`:

```powershell
psql -U admin -d room_counselling -f migrations/006_add_room_assignments_table.sql
```

After running migrations, restart the API server.

---

## Running the API server

Start the FastAPI app with Uvicorn (from project root):

```powershell
python -m uvicorn api:app --reload --host 0.0.0.0 --port 8000
```

The Swagger UI will be available at `http://localhost:8000/docs`.

---

## Important endpoints (quick reference)

All API routes are prefixed with `/api` in `api.py` and `allocation.py` routers.

Allocation session endpoints (in `allocation.py`):

- `POST /api/allocation/session/start` - Start a counselling session (Admin only)
- `POST /api/allocation/session/stop` - Stop session and clear assignments/preferences (Admin only)
- `POST /api/allocation/session/pause` - Pause session (Admin only)
- `POST /api/allocation/session/start-test` - Test-only start without Firebase (deprecated)
- `GET /api/allocation/session/current` - Get current session status
- `POST /api/allocation/select-room` - User selects a room during their turn (authenticated user)
- `POST /api/allocation/clear-all-allocations` - NEW: Clear all allocations & preferences (Admin only)

Assignment endpoints (`api.py`):

- `GET /api/assignments/{user_id}` - Get room assigned to a user (uses `RoomAssignments`)
- `GET /api/assignments/room/{room_id}` - Get all users assigned to a room (returns `assignedUsers` array)

Hostel/room endpoints (`api.py` / `dbconfig/room.py`):

- `GET /api/rooms` - List rooms with filtering
- `GET /api/rooms/{room_id}` - Get room details
- `GET /api/hostels` - Hostel summaries

Authentication:
- Firebase auth endpoints in `firebase_auth.py` (token verification used throughout)

---

## Allocation workflow (how it works)

1. Admin starts a session with `POST /api/allocation/session/start`.
2. Session stores `currentRank` and `turnDuration`.
3. Auto-advance task moves to next rank after time elapses (background task).
4. When it's a user's turn, they call `POST /api/allocation/select-room` with `roomId`.
   - Backend checks room availability, inserts/updates `Preference` (uses ON CONFLICT to avoid duplicates), inserts a `RoomAssignments` row and increments `Rooms.occupied`.
   - If user already has an assignment, backend returns a 400 with a clear message.
5. Session continues until all users processed or admin stops it.

---

## Admin operations

- Start/pause/stop sessions
- Clear all allocations & preferences (new endpoint)
- Stop session will also stop the auto-advance manager

**Clear allocations endpoint:** `POST /api/allocation/clear-all-allocations` (Admin only). This deletes all rows in `RoomAssignments` and `Preference`, resets `Rooms.occupied` to 0, clears deprecated `assignedUserId` fields and unlocks rooms. It does NOT stop the session.

---

## Frontend changes & compatibility

The backend now returns multiple assigned users per room in an `assignedUsers` array.

Important frontend file: `FRONTEND_CHANGES_REQUIRED.md` — share with frontend team. Summary:

- Replace use of `assignedUserId` with `assignedUsers` array
- Remove all price displays / filters (`rentPerSemester`, `pricePerSemester` removed)
- Add an admin button calling `POST /api/allocation/clear-all-allocations` (confirmation required)

---

## Tests

- `run_tests.py` and `run_expanded_tests.py` provide repo-level tests (DB checks and behavior tests).
- Update environment and DB before running tests.

Run tests:

```powershell
python run_tests.py
# or
python run_expanded_tests.py
```

---

## Troubleshooting

- If you see database connection errors, ensure PostgreSQL service is running:

```powershell
Get-Service | Where-Object {$_.Name -like "*postgres*"}
Start-Service postgresql-x64-17
```

- If migration fails, check `apply_migration_006.py` output, check DB user/permissions, and run SQL manually with `psql`.
- If Firebase auth fails, confirm `serviceAccountKey.json` is valid and environment variables are set.

---

## Security & Production notes

- Do NOT commit `serviceAccountKey.json` to source control or public repos.
- Replace default DB credentials before deploying to production.
- Use HTTPS and restrict CORS origins in production.

---

## Contact

For questions, provide context and paste any errors. Point frontend devs to `FRONTEND_CHANGES_REQUIRED.md` for exact changes and examples.

---

_Last updated: November 6, 2025_
