## Hostel Counselling — Backend

This repository contains the backend service for the "Hostel Counselling" application: a system for managing student room counselling and allocation. The backend is written in Python (FastAPI) and exposes REST endpoints used by the frontend to manage sessions, preferences, friends, and the allocation workflow.

---

## Table of Contents

- Project overview
- Key features
- Architecture & major components
- Data model & migrations
- Local development (Windows / PowerShell)
- Running in Docker
- API highlights (important endpoints)
- Admin & allocation workflow
- Scripts and utilities
- Troubleshooting
- Contributing
- License

---

## Project overview

This backend implements the room counselling (allocation) system which supports:

- Firebase authentication integration for users
- Friend-request management and friendship relations
- Preference submission for rooms and roommates per counselling session
- A session-based allocation system (with auto-advance across ranks)
- Room, hostels, blocks and floors metadata and reporting endpoints
- Admin routes to start/stop allocation sessions and clear assignments

The service uses FastAPI to provide a JSON API and PostgreSQL as the primary database.

## Key features

- FastAPI-based REST API (high-performance, asynchronous-compatible)
- Firebase auth integration (server verifies ID tokens from client)
- Counselling sessions with rank-based turns and automatic advancement
- Persistent storage of rooms, users, preferences, room assignments (Postgres)
- Migration SQLs included to initialize and evolve the schema
- Utilities and PowerShell scripts to ease local development on Windows

## Architecture & major components

- `api.py` — FastAPI app initialization, CORS configuration and top-level routers. This file wires together the `firebase_auth`, `friend_requests`, and `allocation` routers and provides many read-only endpoints for hostels, blocks, floors and rooms.
- `allocation.py` — Allocation-related endpoints and the auto-advance background manager that advances the counselling session by rank over time. It also exposes endpoints to start/stop sessions and clear assignments.
- `firebase_auth.py` — Router and helper functions for Firebase token verification and user creation/lookup (used by the frontend for login flows).
- `friend_requests.py` — Router handling friend requests and friend-related operations used by the frontend social workflows.
- `dbconfig/` — A package containing modules that encapsulate DB logic for domain entities:
  - `user.py`, `room.py`, `preference.py`, `counselling_session.py`, `friendship.py`, `queue_management.py` — helper functions and CRUD operations to interact with the Postgres DB.
- `migrations/` — SQL files used to set up and evolve the database schema. See the folder for the initial schema and later incremental changes.

## Data model & migrations

The project includes SQL-based migrations under `migrations/`. Examples found in the repository:

- `000_initial_schema.sql` — base tables (users, rooms, etc.)
- `001_add_counselling_system.sql` — adds counselling session related tables
- `002_add_firebase_auth.sql` — adds schema changes for Firebase integration
- `...` — subsequent migration scripts named sequentially up to `007`

Use those SQL files (or the included helper scripts) to create the database schema before running the service.

## Local development (Windows / PowerShell)

Prerequisites:

- Python 3.10+ (or compatible 3.11)
- PostgreSQL instance (local or remote)
- PowerShell (Windows provided) — repository includes convenience scripts
- A Firebase service account JSON (for server-side verification; see `serviceAccountKey.json` placeholder)

Recommended local steps (PowerShell):

```powershell
# 1. create a virtual environment
python -m venv .venv

# 2. activate it (PowerShell)
. .\.venv\Scripts\Activate.ps1

# 3. install dependencies
pip install -r requirements.txt

# 4. set environment variables (example)
$env:DB_HOST='localhost'
$env:DB_PORT='5432'
$env:DB_NAME='room_counselling'
$env:DB_USER='admin'
$env:DB_PASSWORD='admin123'
# Provide path to your Firebase service account key (or put file at repo root named serviceAccountKey.json)
$env:FIREBASE_CREDENTIALS='c:\path\to\serviceAccountKey.json'

# 5. initialize DB using migrations or helper scripts (see scripts in repo)
# There are PowerShell helper scripts: run_migrations_local.ps1, run_migration_007.ps1, etc.

# 6. run the backend (development)
uvicorn api:app --reload --host 0.0.0.0 --port 8000
```

Notes:

- The repository includes convenience scripts (`run_local.ps1`, `setup_local.ps1`) which may automate some setup steps on Windows. Inspect them before running.
- If using Docker (see next section) you can avoid installing Python locally.

## Running in Docker

There is a `Dockerfile` included for containerized runs. A minimal example to build and run locally:

```powershell
# Build
docker build -t hostel-counselling-backend .

# Run (example) - provide env vars or mount in a .env file
docker run -e DB_HOST=host.docker.internal -e DB_NAME=room_counselling -e DB_USER=admin -e DB_PASSWORD=admin123 -p 8000:8000 hostel-counselling-backend
```

Adjust database connectivity when running from Docker (host.docker.internal or networked Postgres).

## API highlights

The backend exposes many endpoints. Key ones include (non-exhaustive):

- GET `/api/hostels` — list hostels and aggregated room stats
- GET `/api/hostels/{hostelName}` — get a hostel's aggregated stats
- GET `/api/blocks`, `/api/blocks/{hostel}/{block}/floors`, etc. — hierarchical room metadata
- GET `/api/rooms/available` — list available rooms with filters (AC/deluxe/apartment etc.)

Allocation-specific endpoints (prefix `/api/allocation`):

- GET `/api/allocation/session/current` — get current allocation session status
- POST `/api/allocation/session/start` — start a new allocation session (admin-only)
- POST `/api/allocation/session/stop` — stop the active session (admin-only)
- POST `/api/allocation/clear-all-allocations` — clear assignments and preferences (admin-only)

Authentication:

- Routes expect Firebase ID tokens in an `Authorization: Bearer <token>` header for protected routes. The backend verifies tokens using the Firebase admin credentials.

For the full list of endpoints, consult `api.py`, `allocation.py`, `friend_requests.py`, and the router docstrings. When running the server locally with `--reload`, FastAPI will provide interactive docs at `http://localhost:8000/docs`.

## Admin & allocation workflow

- Admins start a counselling session via the allocation endpoint. That creates a session row and a background task (`AllocationAutoAdvance`) which advances user ranks automatically based on a configured `timePerRank` value.
- When the session ends, the service resets preferences and room assignments (depending on the endpoint used) so a fresh allocation cycle can begin.

Important behaviors:

- Auto-advance checks the session's `turnStartTime` against the configured `turnDuration` and advances to the next rank when appropriate.
- Starting a session requires admin role checks (Firebase-authenticated user whose role is `admin`).

## Scripts and utilities

- `run_local.ps1` — helper to run the backend locally (inspect before use)
- `setup_local.ps1` — local setup helper
- `run_migrations_local.ps1`, `run_migration_007.ps1`, `run_migration_007.ps1` — helpers to apply SQL migrations
- `make_admin.py` — convenience script to create an admin user (use with care)

There are also PowerShell helper scripts for converting Firebase data to base64, testing, and migration helpers.

## Frontend integration

The frontend repository lives in the sibling folder `hostel-counselling-frontend`. The frontend uses the API endpoints described above and communicates using Firebase authentication tokens. Typical frontend flow:

1. User signs in with Firebase (client).  
2. Client sends ID token to backend in `Authorization` header.  
3. Backend verifies token and uses or creates a user record, then serves protected endpoints.

When deploying frontend (for example to Vercel), remember to configure the frontend to point to the backend URL and ensure CORS settings are updated accordingly.

## Troubleshooting

- Database connection errors: confirm PostgreSQL is reachable and `DB_*` env vars are set correctly.
- Firebase verification failing: ensure `serviceAccountKey.json` is present and the `FIREBASE_CREDENTIALS` env points to it.
- Port conflicts: the default dev port is 8000 — change with `--port` or in Docker mapping.
- If you encounter unexpected behavior in allocation sessions, check database tables `CounsellingSession`, `User`, `RoomAssignments`, and logs from the background auto-advance task.

## Contributing

Contributions are welcome. Good first steps:

1. Open an issue describing the change or fix.  
2. Create a branch from `main` and submit a PR.  
3. Keep changes small and add unit tests where reasonable.

Coding conventions:

- Python code follows existing project style; keep new modules small and testable.
- Put DB logic inside `dbconfig/` modules where appropriate.

## License

This repository does not currently include a license file. Add one (e.g. MIT) if you plan to make the project public.

---

If you'd like, I can also:

- Add a short `README` to the frontend explaining how to connect to this backend.  
- Create a sample `.env.example` with the recommended environment variables.  
- Add a lightweight smoke test that starts the app and hits `/api/hostels`.

If you want any of those, tell me which and I'll add them next.
# Hostel Counselling Backend# Hostel Counselling Backend# Hostel Counselling Backend



A FastAPI backend for hostel room counselling/allocation system with Firebase authentication.



## 🚀 Deploy on Render - Complete Step-by-Step GuideA FastAPI backend for hostel room counselling/allocation system with Firebase authentication.A FastAPI backend that implements a hostel room counselling/allocation system with Firebase authentication and a denormalized `Rooms` table. It supports a timed counselling session where users pick rooms in rank order, preference tracking, room locking, and admin operations.



### Prerequisites

- GitHub account with this repository pushed

- Render account (sign up at [render.com](https://render.com))## Deployment on RenderThis README explains the project architecture, how to set it up locally on Windows, database migrations, important endpoints (including admin endpoints), how allocation works, testing, and frontend compatibility notes.

- Firebase project with service account key



---

### Environment Variables---

### Step 1: Prepare Firebase Service Account



1. **Get your Firebase service account JSON file**:

   - Go to Firebase Console → Project Settings → Service AccountsSet the following environment variables in Render:## Table of Contents

   - Click "Generate New Private Key"

   - Download the JSON file



2. **Convert to Base64** (for secure storage as environment variable):```- Project overview

   ```powershell

   # On Windows PowerShellDB_HOST=<your-postgres-host>- Key concepts and data model

   $content = Get-Content serviceAccountKey.json -Raw

   $bytes = [System.Text.Encoding]::UTF8.GetBytes($content)DB_PORT=5432- Repo layout

   $base64 = [Convert]::ToBase64String($bytes)

   $base64 | Set-ClipboardDB_NAME=room_counselling- Requirements

   # Base64 string is now in your clipboard

   ```DB_USER=<your-db-user>- Local setup (Windows PowerShell)



---DB_PASSWORD=<your-db-password>- Database & migrations



### Step 2: Push Code to GitHub```- Running the API server



1. **Add `.gitignore` entry** (if not already there):- Important endpoints (quick reference)

   ```

   serviceAccountKey.json### Build Command- Allocation workflow

   .venv/

   __pycache__/- Admin operations (clear allocations, stop session, etc.)

   *.pyc

   ``````bash- Frontend changes and compatibility



2. **Commit and push**:pip install -r requirements.txt- Tests

   ```powershell

   git add .```- Troubleshooting

   git commit -m "Prepare for Render deployment"

   git push origin main

   ```

### Start Command---

---



### Step 3: Create PostgreSQL Database on Render

```bash## Project overview

1. Log in to [Render Dashboard](https://dashboard.render.com)

2. Click **"New +"** → **"PostgreSQL"**uvicorn api:app --host 0.0.0.0 --port $PORT

3. Configure database:

   - **Name**: `hostel-counselling-db` (or your choice)```This service implements a hostel room allocation/counselling system where:

   - **Database**: `room_counselling`

   - **User**: Auto-generated

   - **Region**: Choose closest to your users (e.g., Singapore, Oregon)

   - **Plan**: Free tier (or paid for better performance)### Database Setup- Users are given ranks and have a limited time per rank to choose a room.

4. Click **"Create Database"**

5. **IMPORTANT**: Copy the **"Internal Database URL"** - you'll need this- Preferences are recorded (and can be migrated/updated).

   - Format: `postgresql://user:password@host/database`

   - Find it in the database dashboard under "Connections"1. Create a PostgreSQL database on Render- Rooms are stored in a denormalized `Rooms` table for fast lookups.



---2. Run migrations in order from the `migrations/` folder- Room assignments are tracked in a `RoomAssignments` table (one row per user-room assignment).



### Step 4: Deploy Web Service on Render3. Ensure Firebase service account key is properly configured- Rooms can be locked for a user while they decide.



1. Go to [Render Dashboard](https://dashboard.render.com)- Admins can start/pause/stop sessions and clear allocations.

2. Click **"New +"** → **"Web Service"**

3. **Connect your GitHub repository**:### Important Files- Firebase is used for authentication and role-based access (admin/user).

   - Click "Connect account" if first time

   - Select your `hostel-counselling-backend` repository

4. Configure service:

   - **Name**: `hostel-counselling-backend` (or your choice)- `api.py` - Main FastAPI application---

   - **Region**: **Same as your database** (important for low latency)

   - **Branch**: `main`- `allocation.py` - Allocation session logic

   - **Root Directory**: (leave empty)

   - **Runtime**: `Python 3`- `firebase_auth.py` - Firebase authentication## Key concepts and data model

   - **Build Command**: 

     ```- `dbconfig/` - Database configuration and models

     pip install -r requirements.txt

     ```- `migrations/` - SQL migration filesImportant tables (denormalized):

   - **Start Command**: 

     ```- `requirements.txt` - Python dependencies

     uvicorn api:app --host 0.0.0.0 --port $PORT

     ```- `Dockerfile` - Docker configuration- `Rooms` - denormalized table containing room metadata and occupancy (`capacity`, `occupied`).

   - **Plan**: Free (or paid for better performance)

- `RoomAssignments` - new table (migration 006) that stores one row per assignment: (`roomId`, `userId`, `assignedAt`).

5. **Add Environment Variables** (click "Advanced" → "Add Environment Variable"):

### Notes- `Preference` - tracks user preference selections per session.

   | Key | Value | Notes |

   |-----|-------|-------|- `User` - user records (including `rank`, `role`, etc.).

   | `DATABASE_URL` | `postgresql://user:pass@host/db` | Copy "Internal Database URL" from Step 3 |

   | `FIREBASE_SERVICE_ACCOUNT_BASE64` | `eyJ0eXBlIjoi...` | Paste Base64 string from Step 1 |- **IMPORTANT**: Do not commit `serviceAccountKey.json` to public repositories- `CounsellingSession` - session control (active/completed, current rank, timing).

   | `PYTHON_VERSION` | `3.12.0` | Specify Python version |

- Update database credentials before deployment

6. Click **"Create Web Service"**

- Use HTTPS in productionNotes:

7. **Watch the deployment** (5-10 minutes):

   - View logs in real-time- Configure CORS origins appropriately- `Rooms.assignedUserId` exists for backward compatibility but is deprecated. Use `RoomAssignments`.

   - Look for "Application startup complete"

   - Note any errors- Price/fee fields (`rentPerSemester`, `pricePerSemester`) have been removed by request.



8. **Save your service URL**:---

   - Something like: `https://hostel-counselling-backend-xyz.onrender.com`

## Repo layout (important files)

---

- `api.py` - Main FastAPI app and many endpoints

### Step 5: Run Database Migrations- `allocation.py` - Allocation session endpoints and logic

- `dbconfig/room.py` - DB helpers for rooms and assignment operations

After your web service is deployed, run migrations:- `migrations/` - SQL migration files (see 005, 006)

- `apply_migration_006.py` - convenience script to apply migration 006

1. In Render dashboard, go to your web service- `run_tests.py`, `run_expanded_tests.py` - included test scripts

2. Click the **"Shell"** tab (top navigation)- `FRONTEND_CHANGES_REQUIRED.md` - guidance for frontend updates after API changes

3. Wait for shell to connect- `requirements.txt` - Python package requirements

4. Run migrations **in order**:- `serviceAccountKey.json` - Firebase credentials (sensitive - DO NOT commit publicly)



```bash---

# Run each migration one by one

psql $DATABASE_URL -f migrations/000_initial_schema.sql## Requirements

psql $DATABASE_URL -f migrations/001_add_counselling_system.sql

psql $DATABASE_URL -f migrations/002_add_firebase_auth.sql- Python 3.10+ (project used 3.12 in dev environment)

psql $DATABASE_URL -f migrations/003_cleanup_user_table.sql- PostgreSQL (local or remote)

psql $DATABASE_URL -f migrations/004_add_user_role.sql- pip packages in `requirements.txt`

psql $DATABASE_URL -f migrations/005_denormalize_to_rooms_table.sql- Firebase project configuration for authentication

psql $DATABASE_URL -f migrations/006_add_room_assignments_table.sql

```---



5. **Verify migrations**:## Local setup (Windows PowerShell)

```bash

psql $DATABASE_URL -c "\dt"  # List all tables1. Create or activate a Python environment and install dependencies:

```

```powershell

You should see tables like: `Rooms`, `RoomAssignments`, `User`, `Preference`, `CounsellingSession`, etc.# Using pyenv/venv as appropriate. Example:

python -m venv .venv

---.\.venv\Scripts\Activate.ps1

python -m pip install -r requirements.txt

### Step 6: Update Firebase Configuration```



Update `firebase_auth.py` to handle Base64 environment variable:2. Configure database connection in `dbconfig/room.py` or `allocation.py` if using different DB settings. Default DB_CONFIG in code is:



1. The code should decode the Base64 service account key```python

2. This is already handled if you use the provided configurationDB_CONFIG = {

  'host': 'localhost',

---  'port': 5432,

  'database': 'room_counselling',

### Step 7: Verify Deployment  'user': 'admin',

  'password': 'admin123'

1. **Test API Documentation**:}

   - Visit: `https://your-service.onrender.com/docs````

   - You should see FastAPI Swagger UI

Change credentials before deploying to production.

2. **Test a simple endpoint**:

   ```bash3. Ensure PostgreSQL is running. On Windows you may need to start the service:

   curl https://your-service.onrender.com/api/hostels

   ``````powershell

# Run as Administrator if needed

3. **Check health**:Start-Service postgresql-x64-17

   - Your service should show "Live" status in Render dashboard```



------



### Step 8: Update CORS Origins (Production Security)## Database & migrations



1. Edit `api.py` in your code:This repo stores schema changes as SQL in `migrations/`.



```pythonKey migration: `migrations/006_add_room_assignments_table.sql` - creates the `RoomAssignments` table and migrates existing assignments.

# Change from:

allow_origins=["*"]To apply migration 006 (convenience script included):



# To:```powershell

allow_origins=[python apply_migration_006.py

    "https://your-frontend-domain.com",  # Your actual frontend URL```

    "http://localhost:3000",  # For local development only

]Or run directly with `psql`:

```

```powershell

2. Commit and push:psql -U admin -d room_counselling -f migrations/006_add_room_assignments_table.sql

```powershell```

git add api.py

git commit -m "Update CORS for production"After running migrations, restart the API server.

git push origin main

```---



3. Render will automatically redeploy (watch the logs)## Running the API server



---Start the FastAPI app with Uvicorn (from project root):



### Step 9: Create Admin User```powershell

python -m uvicorn api:app --reload --host 0.0.0.0 --port 8000

1. Go to Render Shell for your web service```

2. Run the admin creation script:

The Swagger UI will be available at `http://localhost:8000/docs`.

```bash

python make_admin.py---

```

## Important endpoints (quick reference)

Or create via database:

All API routes are prefixed with `/api` in `api.py` and `allocation.py` routers.

```bash

psql $DATABASE_URLAllocation session endpoints (in `allocation.py`):

# Then in psql:

UPDATE "User" SET role = 'admin' WHERE email = 'your-email@example.com';- `POST /api/allocation/session/start` - Start a counselling session (Admin only)

```- `POST /api/allocation/session/stop` - Stop session and clear assignments/preferences (Admin only)

- `POST /api/allocation/session/pause` - Pause session (Admin only)

---- `POST /api/allocation/session/start-test` - Test-only start without Firebase (deprecated)

- `GET /api/allocation/session/current` - Get current session status

## Environment Variables Reference- `POST /api/allocation/select-room` - User selects a room during their turn (authenticated user)

- `POST /api/allocation/clear-all-allocations` - NEW: Clear all allocations & preferences (Admin only)

| Variable | Required | Description | Example |

|----------|----------|-------------|---------|Assignment endpoints (`api.py`):

| `DATABASE_URL` | ✅ Yes | PostgreSQL connection (Render provides this) | `postgresql://user:pass@host/db` |

| `FIREBASE_SERVICE_ACCOUNT_BASE64` | ✅ Yes | Base64-encoded Firebase JSON | Long base64 string |- `GET /api/assignments/{user_id}` - Get room assigned to a user (uses `RoomAssignments`)

| `PYTHON_VERSION` | Recommended | Python version | `3.12.0` |- `GET /api/assignments/room/{room_id}` - Get all users assigned to a room (returns `assignedUsers` array)



---Hostel/room endpoints (`api.py` / `dbconfig/room.py`):



## Monitoring & Maintenance- `GET /api/rooms` - List rooms with filtering

- `GET /api/rooms/{room_id}` - Get room details

### View Logs- `GET /api/hostels` - Hostel summaries

- Render Dashboard → Your Service → "Logs" tab

- Real-time logs with filteringAuthentication:

- Firebase auth endpoints in `firebase_auth.py` (token verification used throughout)

### Restart Service

- Render Dashboard → "Manual Deploy" → "Deploy latest commit"---

- Or: "Clear build cache & deploy" for clean restart

## Allocation workflow (how it works)

### Database Access

- Render Dashboard → PostgreSQL Database → "Connect" tab1. Admin starts a session with `POST /api/allocation/session/start`.

- Use provided connection strings2. Session stores `currentRank` and `turnDuration`.

3. Auto-advance task moves to next rank after time elapses (background task).

### Shell Access4. When it's a user's turn, they call `POST /api/allocation/select-room` with `roomId`.

- Render Dashboard → Your Service → "Shell" tab   - Backend checks room availability, inserts/updates `Preference` (uses ON CONFLICT to avoid duplicates), inserts a `RoomAssignments` row and increments `Rooms.occupied`.

- Full Linux shell in your service container   - If user already has an assignment, backend returns a 400 with a clear message.

5. Session continues until all users processed or admin stops it.

---

---

## Common Issues & Solutions

## Admin operations

### ❌ Issue: "Application failed to start"

**Solution**: - Start/pause/stop sessions

- Check Render logs for specific error- Clear all allocations & preferences (new endpoint)

- Verify `DATABASE_URL` is set- Stop session will also stop the auto-advance manager

- Ensure all dependencies are in `requirements.txt`

**Clear allocations endpoint:** `POST /api/allocation/clear-all-allocations` (Admin only). This deletes all rows in `RoomAssignments` and `Preference`, resets `Rooms.occupied` to 0, clears deprecated `assignedUserId` fields and unlocks rooms. It does NOT stop the session.

### ❌ Issue: "Database connection refused"

**Solution**:---

- Use "Internal Database URL" not "External"

- Verify database and web service are in same region## Frontend changes & compatibility

- Check database is running (Render dashboard)

The backend now returns multiple assigned users per room in an `assignedUsers` array.

### ❌ Issue: "Firebase authentication fails"

**Solution**:Important frontend file: `FRONTEND_CHANGES_REQUIRED.md` — share with frontend team. Summary:

- Verify `FIREBASE_SERVICE_ACCOUNT_BASE64` is set correctly

- Test Base64 encoding/decoding locally first- Replace use of `assignedUserId` with `assignedUsers` array

- Check Firebase project settings- Remove all price displays / filters (`rentPerSemester`, `pricePerSemester` removed)

- Add an admin button calling `POST /api/allocation/clear-all-allocations` (confirmation required)

### ❌ Issue: "Migrations fail"

**Solution**:---

- Run migrations in exact order (000 → 006)

- Check for existing tables: `psql $DATABASE_URL -c "\dt"`## Tests

- Verify database permissions

- `run_tests.py` and `run_expanded_tests.py` provide repo-level tests (DB checks and behavior tests).

### ❌ Issue: "Service times out / slow"- Update environment and DB before running tests.

**Solution**:

- Free tier services sleep after 15 min of inactivityRun tests:

- Consider upgrading to paid plan

- First request after sleep takes ~30 seconds```powershell

python run_tests.py

---# or

python run_expanded_tests.py

## Local Development```



```powershell---

# 1. Clone repository

git clone https://github.com/your-username/hostel-counselling-backend.git## Troubleshooting

cd hostel-counselling-backend

- If you see database connection errors, ensure PostgreSQL service is running:

# 2. Create virtual environment

python -m venv .venv```powershell

.\.venv\Scripts\Activate.ps1Get-Service | Where-Object {$_.Name -like "*postgres*"}

Start-Service postgresql-x64-17

# 3. Install dependencies```

pip install -r requirements.txt

- If migration fails, check `apply_migration_006.py` output, check DB user/permissions, and run SQL manually with `psql`.

# 4. Set up local PostgreSQL- If Firebase auth fails, confirm `serviceAccountKey.json` is valid and environment variables are set.

# Create database: room_counselling

# Update credentials in dbconfig/room.py---



# 5. Run migrations locally## Security & Production notes

psql -U admin -d room_counselling -f migrations/000_initial_schema.sql

# ... run all migrations- Do NOT commit `serviceAccountKey.json` to source control or public repos.

- Replace default DB credentials before deploying to production.

# 6. Run server- Use HTTPS and restrict CORS origins in production.

uvicorn api:app --reload --host 0.0.0.0 --port 8000

---

# 7. Visit http://localhost:8000/docs

```## Contact



---For questions, provide context and paste any errors. Point frontend devs to `FRONTEND_CHANGES_REQUIRED.md` for exact changes and examples.



## Project Structure---



```_Last updated: November 6, 2025_

├── api.py                      # Main FastAPI app
├── allocation.py               # Allocation session logic
├── firebase_auth.py            # Firebase authentication
├── friend_requests.py          # Friend request handlers
├── make_admin.py              # Admin utility script
├── config.py                  # Environment configuration
├── requirements.txt           # Python dependencies
├── Dockerfile                 # Docker configuration
├── .gitignore                # Git ignore rules
├── dbconfig/                  # Database modules
│   ├── __init__.py
│   ├── counselling_session.py
│   ├── friendship.py
│   ├── preference.py
│   ├── queue_management.py
│   ├── room.py
│   └── user.py
└── migrations/                # SQL migrations (run in order!)
    ├── 000_initial_schema.sql
    ├── 001_add_counselling_system.sql
    ├── 002_add_firebase_auth.sql
    ├── 003_cleanup_user_table.sql
    ├── 004_add_user_role.sql
    ├── 005_denormalize_to_rooms_table.sql
    └── 006_add_room_assignments_table.sql
```

---

## API Endpoints Overview

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - User login
- `GET /api/auth/verify` - Verify token

### Allocation
- `POST /api/allocation/session/start` - Start counselling (Admin)
- `POST /api/allocation/session/stop` - Stop session (Admin)
- `GET /api/allocation/session/current` - Get session status
- `POST /api/allocation/select-room` - Select a room

### Rooms & Hostels
- `GET /api/rooms` - List all rooms
- `GET /api/rooms/{room_id}` - Get room details
- `GET /api/hostels` - List hostels

### Assignments
- `GET /api/assignments/{user_id}` - Get user's assignment
- `GET /api/assignments/room/{room_id}` - Get room's assignments

Full API docs: `https://your-service.onrender.com/docs`

---

## Security Checklist ✅

- [ ] `serviceAccountKey.json` is in `.gitignore`
- [ ] Never committed `serviceAccountKey.json` to Git
- [ ] Used Base64 encoding for Firebase key in environment
- [ ] Changed CORS from `["*"]` to specific origins
- [ ] Database credentials stored in Render environment variables
- [ ] Using HTTPS (Render provides automatically)
- [ ] PostgreSQL database has strong password
- [ ] Admin users properly configured

---

## Performance Tips

1. **Database Indexing**: Ensure migrations create proper indexes
2. **Connection Pooling**: Consider `psycopg2-pool` for production
3. **Caching**: Add Redis for session caching (optional)
4. **Paid Plan**: Render free tier sleeps after inactivity
5. **Region Selection**: Deploy database and service in same region

---

## Useful Links

- **Render Dashboard**: https://dashboard.render.com
- **Render Docs**: https://render.com/docs
- **FastAPI Docs**: https://fastapi.tiangolo.com
- **Firebase Console**: https://console.firebase.google.com
- **PostgreSQL Docs**: https://www.postgresql.org/docs/

---

## Next Steps After Deployment

1. ✅ Test all endpoints via Swagger UI
2. ✅ Create admin user
3. ✅ Configure frontend to use your API URL
4. ✅ Set up monitoring/alerts (Render provides basic monitoring)
5. ✅ Add custom domain (optional, requires paid plan)
6. ✅ Set up CI/CD (Render auto-deploys on push)

---

## Support

If you encounter issues:
1. Check Render logs first
2. Verify all environment variables
3. Test endpoints via Swagger UI
4. Check database connectivity in Shell

---

**🎉 Your API is now live and ready for production use!**

_Last updated: November 10, 2025_
