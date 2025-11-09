# 🚀 Render Deployment Checklist

Use this checklist to ensure smooth deployment to Render.

## Pre-Deployment ✅

- [ ] Firebase service account JSON file downloaded from Firebase Console
- [ ] Converted Firebase JSON to Base64 using `convert_firebase_to_base64.ps1`
- [ ] Code pushed to GitHub repository
- [ ] `serviceAccountKey.json` is in `.gitignore` (already done ✓)
- [ ] Reviewed `requirements.txt` - all dependencies listed

## Render Setup ✅

### Database Setup
- [ ] Created PostgreSQL database on Render
- [ ] Noted database name: `room_counselling`
- [ ] Copied "Internal Database URL" for later use
- [ ] Database region selected (e.g., Singapore, Oregon)

### Web Service Setup
- [ ] Created new Web Service on Render
- [ ] Connected GitHub repository
- [ ] Selected correct branch: `main`
- [ ] Set Runtime: `Python 3`
- [ ] Set Build Command: `pip install -r requirements.txt`
- [ ] Set Start Command: `uvicorn api:app --host 0.0.0.0 --port $PORT`
- [ ] Selected same region as database

### Environment Variables
- [ ] Added `DATABASE_URL` (from PostgreSQL Internal URL)
- [ ] Added `FIREBASE_SERVICE_ACCOUNT_BASE64` (from conversion script)
- [ ] Added `PYTHON_VERSION` = `3.12.0`

### Deployment
- [ ] Clicked "Create Web Service"
- [ ] Watched build logs for errors
- [ ] Service shows "Live" status
- [ ] Noted service URL: `https://_____.onrender.com`

## Post-Deployment ✅

### Run Migrations
- [ ] Opened Render Shell for web service
- [ ] Ran migration 000: `psql $DATABASE_URL -f migrations/000_initial_schema.sql`
- [ ] Ran migration 001: `psql $DATABASE_URL -f migrations/001_add_counselling_system.sql`
- [ ] Ran migration 002: `psql $DATABASE_URL -f migrations/002_add_firebase_auth.sql`
- [ ] Ran migration 003: `psql $DATABASE_URL -f migrations/003_cleanup_user_table.sql`
- [ ] Ran migration 004: `psql $DATABASE_URL -f migrations/004_add_user_role.sql`
- [ ] Ran migration 005: `psql $DATABASE_URL -f migrations/005_denormalize_to_rooms_table.sql`
- [ ] Ran migration 006: `psql $DATABASE_URL -f migrations/006_add_room_assignments_table.sql`
- [ ] Verified tables: `psql $DATABASE_URL -c "\dt"`

### Testing
- [ ] Visited Swagger UI: `https://your-service.onrender.com/docs`
- [ ] Tested `/api/hostels` endpoint
- [ ] Checked logs for any errors
- [ ] Verified Firebase authentication works

### Security & Configuration
- [ ] Updated CORS origins in `api.py` (remove `["*"]`)
- [ ] Pushed CORS changes to GitHub
- [ ] Verified auto-deployment worked
- [ ] Created admin user via `make_admin.py` in Shell

### Final Steps
- [ ] Documented service URL for frontend team
- [ ] Tested key endpoints with frontend
- [ ] Set up monitoring/alerts (optional)
- [ ] Added custom domain (optional, requires paid plan)

## Troubleshooting Commands ✅

If you encounter issues, use these commands in Render Shell:

```bash
# Check database connection
psql $DATABASE_URL -c "SELECT version();"

# List all tables
psql $DATABASE_URL -c "\dt"

# Check Python version
python --version

# Check environment variables
echo $DATABASE_URL
env | grep FIREBASE

# Test database query
psql $DATABASE_URL -c "SELECT COUNT(*) FROM \"Rooms\";"

# View recent logs
# (Use Render Dashboard → Logs tab)
```

## Common Issues & Quick Fixes ✅

### Service won't start
- Check Render logs for specific error
- Verify all environment variables are set
- Ensure `DATABASE_URL` uses Internal URL

### Database connection failed
- Confirm database and service in same region
- Check database status in Render dashboard
- Verify connection string format

### Firebase errors
- Confirm Base64 string is complete (no truncation)
- Test conversion script again
- Check Firebase project is active

### Slow first request
- Normal for free tier (spins down after 15 min)
- Consider paid plan for always-on service

## Notes 📝

- **Free Tier Limitations**: 
  - Service spins down after 15 minutes of inactivity
  - Database has 90-day data retention
  - 750 hours/month free
  
- **Auto-Deploy**: 
  - Render automatically deploys when you push to `main` branch
  
- **Logs**: 
  - Available in Render Dashboard → Logs tab
  - Real-time streaming
  - Searchable and filterable

---

**✅ Deployment Complete!** 

Your backend is now live at: `https://your-service.onrender.com`

API Documentation: `https://your-service.onrender.com/docs`
