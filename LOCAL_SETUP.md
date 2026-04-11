# Local Development Setup Guide

This guide will help you set up and run the Hostel Counselling System locally on Windows.

## Prerequisites

1. **Python 3.12+** - [Download here](https://www.python.org/downloads/)
2. **PostgreSQL 14+** - [Download here](https://www.postgresql.org/download/windows/)
3. **Node.js 18+** and npm - [Download here](https://nodejs.org/)
4. **Git** - [Download here](https://git-scm.com/downloads)
5. **Firebase Project** - Set up at [Firebase Console](https://console.firebase.google.com/)

## Step 1: Database Setup

### Install PostgreSQL

1. Download and install PostgreSQL from the link above
2. During installation, remember the password you set for the `postgres` user
3. Default port is `5432` - keep it unless you have a conflict

### Create Database

Open PowerShell or Command Prompt and run:

```powershell
# Connect to PostgreSQL
psql -U postgres

# Create database (in psql prompt)
CREATE DATABASE room_counselling;

# Exit psql
\q
```

Alternatively, you can use pgAdmin (comes with PostgreSQL):
1. Open pgAdmin
2. Right-click on Databases → Create → Database
3. Name it `room_counselling`

### Run Migrations

After setting up the backend (Step 2), run the migrations:

```powershell
cd hostel-counselling-backend

# Connect to PostgreSQL and run migrations
psql -U postgres -d room_counselling -f migrations/000_initial_schema.sql
psql -U postgres -d room_counselling -f migrations/001_add_counselling_system.sql
psql -U postgres -d room_counselling -f migrations/002_add_firebase_auth.sql
psql -U postgres -d room_counselling -f migrations/003_cleanup_user_table.sql
psql -U postgres -d room_counselling -f migrations/004_add_user_role.sql
psql -U postgres -d room_counselling -f migrations/005_denormalize_to_rooms_table.sql
psql -U postgres -d room_counselling -f migrations/006_add_room_assignments_table.sql
```

Or use the provided script:
```powershell
.\run_migrations_local.ps1
```

## Step 2: Backend Setup

### Clone Repository (if not already done)

```powershell
cd C:\Users\Prasad\Documents\GitHub
git clone https://github.com/ved-bankeshwar/hostel-counselling-backend.git
cd hostel-counselling-backend
```

### Create Virtual Environment

```powershell
# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# If you get an execution policy error, run:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Install Dependencies

```powershell
pip install -r requirements.txt
```

### Configure Environment Variables

1. Copy `.env.example` to `.env.local`:
```powershell
cp .env.example .env.local
```

2. Edit `.env.local` and update the values:
   - Update `DB_PASSWORD` to match your PostgreSQL password
   - Add your Firebase credentials (see Firebase Setup section)

### Firebase Setup

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Select your project or create a new one
3. Go to Project Settings → Service Accounts
4. Click "Generate New Private Key"
5. Save the file as `serviceAccountKey.json` in the backend root directory

**Option 1: Use Base64 (Recommended for deployment)**
```powershell
# Convert to base64
$content = Get-Content serviceAccountKey.json -Raw
$bytes = [System.Text.Encoding]::UTF8.GetBytes($content)
$base64 = [Convert]::ToBase64String($bytes)
$base64 | Set-Clipboard
# Now paste this into FIREBASE_SERVICE_ACCOUNT_BASE64 in .env.local
```

**Option 2: Use file directly (Easier for local development)**
- Just keep `serviceAccountKey.json` in the root directory
- The app will automatically detect and use it

### Start the Backend Server

```powershell
# Make sure virtual environment is activated
# Run the server
uvicorn api:app --reload --host 0.0.0.0 --port 8000
```

Or use the provided script:
```powershell
.\run_local.ps1
```

The backend will be available at: `http://localhost:8000`

API Documentation: `http://localhost:8000/docs`

## Step 3: Frontend Setup

### Navigate to Frontend Directory

```powershell
cd ..\hostel-counselling-frontend\room_counselling
```

### Install Dependencies

```powershell
npm install
```

### Configure Environment Variables

1. Copy `.env.example` to `.env.local`:
```powershell
cp .env.example .env.local
```

2. Edit `.env.local` and update:
```env
NEXT_PUBLIC_FIREBASE_API_KEY=your_firebase_api_key
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=your_project.firebaseapp.com
NEXT_PUBLIC_FIREBASE_PROJECT_ID=your_project_id
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=your_project.firebasestorage.app
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=your_sender_id
NEXT_PUBLIC_FIREBASE_APP_ID=your_app_id
NEXT_PUBLIC_FIREBASE_MEASUREMENT_ID=your_measurement_id
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

**Important:** Change `NEXT_PUBLIC_API_BASE_URL` to `http://localhost:8000` for local development

You can find these Firebase config values in:
Firebase Console → Project Settings → General → Your apps → SDK setup and configuration

### Start the Frontend Server

```powershell
npm run dev
```

The frontend will be available at: `http://localhost:3000`

## Step 4: Verify Everything Works

1. **Backend Health Check:**
   - Open `http://localhost:8000/docs`
   - You should see the FastAPI Swagger documentation

2. **Frontend:**
   - Open `http://localhost:3000`
   - You should see the login page

3. **Test Registration:**
   - Try creating a new account
   - Check if you can log in

## Common Issues

### PostgreSQL Connection Error

**Error:** `could not connect to server`

**Solutions:**
- Check if PostgreSQL service is running (Services → PostgreSQL)
- Verify port 5432 is not blocked by firewall
- Check credentials in `.env.local`

### Python Virtual Environment

**Error:** `cannot be loaded because running scripts is disabled`

**Solution:**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Port Already in Use

**Error:** `Address already in use`

**Solution for Backend (Port 8000):**
```powershell
# Find process using port 8000
netstat -ano | findstr :8000
# Kill the process (replace PID with actual process ID)
taskkill /PID <PID> /F
```

**Solution for Frontend (Port 3000):**
```powershell
# Find process using port 3000
netstat -ano | findstr :3000
# Kill the process
taskkill /PID <PID> /F
```

### Firebase Authentication Not Working

**Issues:**
- Check if Firebase config is correct in frontend `.env.local`
- Verify `serviceAccountKey.json` is present in backend
- Check Firebase Console → Authentication is enabled

## Development Workflow

### Running Both Servers

**Terminal 1 (Backend):**
```powershell
cd hostel-counselling-backend
.\venv\Scripts\Activate.ps1
uvicorn api:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 (Frontend):**
```powershell
cd hostel-counselling-frontend\room_counselling
npm run dev
```

### Making Database Changes

1. Create a new migration file in `migrations/` folder
2. Run the migration:
```powershell
psql -U postgres -d room_counselling -f migrations/YOUR_NEW_MIGRATION.sql
```

### Testing API Endpoints

Use the Swagger UI at `http://localhost:8000/docs` or use PowerShell:

```powershell
# Example: Get all hostels
Invoke-RestMethod -Uri "http://localhost:8000/api/hostels" -Method GET
```

## Quick Start Scripts

### Backend Start Script (`run_local.ps1`)

Already available in the repository - just run:
```powershell
.\run_local.ps1
```

### Frontend Start Script

Create `run_frontend.ps1` in the frontend directory:
```powershell
cd room_counselling
npm run dev
```

## Environment Files Summary

### Backend `.env.local`
- Database credentials (local PostgreSQL)
- Firebase service account (base64 or file path)
- Server port

### Frontend `.env.local`
- Firebase web app configuration
- API base URL (http://localhost:8000 for local)

## Next Steps

1. ✅ Database created and migrations run
2. ✅ Backend running on port 8000
3. ✅ Frontend running on port 3000
4. ✅ Firebase configured
5. 🎉 Start developing!

## Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Next.js Documentation](https://nextjs.org/docs)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Firebase Documentation](https://firebase.google.com/docs)
