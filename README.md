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
