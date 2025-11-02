# Firebase Authentication Setup Guide

## Overview
The backend now supports Firebase Authentication with Google Sign-In. Users authenticate via Firebase on the frontend, and the backend verifies Firebase ID tokens to authenticate API requests.

---

## What's Been Updated

### 1. Database Schema
✅ User table now includes Firebase authentication fields:
- `firebase_uid` - Unique Firebase user ID (indexed)
- `email` - User email from Google Sign-In (indexed)
- `display_name` - User's full name from Google
- `photo_url` - Profile photo URL from Google
- `registration_number` - Student registration number (set later)
- `provider` - Authentication provider ('google')
- `last_login_at` - Last login timestamp
- `created_at` - Account creation timestamp
- `updated_at` - Last profile update timestamp

### 2. API Endpoints

#### `POST /api/auth/firebase`
Verify Firebase token and create/update user.

**Request:**
```http
POST /api/auth/firebase
Authorization: Bearer <firebase_id_token>
Content-Type: application/json

{
  "firebase_uid": "abc123xyz...",
  "email": "student@example.com",
  "display_name": "John Doe",
  "photo_url": "https://lh3.googleusercontent.com/..."
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "firebase_uid": "abc123xyz...",
    "email": "student@example.com",
    "display_name": "John Doe",
    "name": "John Doe",
    "photo_url": "https://...",
    "registration_number": null,
    "gender": "male",
    "rank": 1,
    "hostel": "Hostel A",
    "is_active": true,
    "provider": "google",
    "last_login_at": "2025-11-01T10:30:00",
    "created_at": "2025-01-15T08:00:00"
  },
  "message": "User logged in successfully"
}
```

#### `GET /api/auth/me`
Get current authenticated user's profile.

**Request:**
```http
GET /api/auth/me
Authorization: Bearer <firebase_id_token>
```

**Response:**
```json
{
  "id": 1,
  "firebase_uid": "abc123xyz...",
  "email": "student@example.com",
  "display_name": "John Doe",
  "registration_number": "2021CS001",
  ...
}
```

#### `PATCH /api/auth/me`
Update user profile.

**Request:**
```http
PATCH /api/auth/me
Authorization: Bearer <firebase_id_token>
Content-Type: application/json

{
  "registration_number": "2021CS001",
  "display_name": "John Doe Updated"
}
```

#### `GET /api/auth/user/{firebase_uid}`
Get user by Firebase UID (public endpoint).

---

## Firebase Admin SDK Setup

### 1. Install Dependencies
✅ Already installed: `firebase-admin==6.2.0`

```bash
pip install firebase-admin==6.2.0
```

### 2. Get Firebase Service Account Key

#### Steps:
1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Select your project: **roomcounselling**
3. Click ⚙️ Settings → **Project settings**
4. Go to **Service accounts** tab
5. Click **Generate new private key**
6. Download the JSON file
7. **Rename it to `serviceAccountKey.json`**
8. **Place it in your project root directory:**
   ```
   hostel-counselling-backend/
   ├── serviceAccountKey.json  ← Place here
   ├── api.py
   ├── firebase_auth.py
   ├── requirements.txt
   └── ...
   ```

#### ⚠️ IMPORTANT SECURITY NOTES:
- **DO NOT commit `serviceAccountKey.json` to Git**
- Add it to `.gitignore`:
  ```gitignore
  # Firebase
  serviceAccountKey.json
  ```
- In production, use environment variables or secret management systems

### 3. Environment Variables (Optional)

If you want to place the service account key elsewhere:

```bash
# Windows PowerShell
$env:FIREBASE_SERVICE_ACCOUNT_PATH="C:\path\to\serviceAccountKey.json"

# Linux/Mac
export FIREBASE_SERVICE_ACCOUNT_PATH="/path/to/serviceAccountKey.json"
```

Or add to `.env` file:
```env
FIREBASE_SERVICE_ACCOUNT_PATH=/path/to/serviceAccountKey.json
```

---

## Testing the Setup

### 1. Start the Backend
```bash
python -m uvicorn api:app --reload --port 8000
```

You should see:
```
✅ Firebase Admin SDK initialized from serviceAccountKey.json
INFO:     Application startup complete.
```

### 2. Test with cURL

```bash
# Get a Firebase ID token from your frontend first
# Then test the endpoint:

curl -X POST http://localhost:8000/api/auth/firebase \
  -H "Authorization: Bearer <YOUR_FIREBASE_ID_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "firebase_uid": "YOUR_FIREBASE_UID",
    "email": "your@email.com",
    "display_name": "Your Name",
    "photo_url": "https://your-photo-url.com"
  }'
```

### 3. Check API Documentation
Visit http://localhost:8000/docs to see all Firebase auth endpoints in Swagger UI.

---

## Frontend Integration

### Example: Next.js with Firebase

```typescript
// Frontend code (Next.js/React)
import { auth } from '@/lib/firebase';
import { signInWithPopup, GoogleAuthProvider } from 'firebase/auth';

async function signInWithGoogle() {
  try {
    // 1. Sign in with Firebase
    const provider = new GoogleAuthProvider();
    const result = await signInWithPopup(auth, provider);
    const user = result.user;
    
    // 2. Get Firebase ID token
    const idToken = await user.getIdToken();
    
    // 3. Send to backend
    const response = await fetch('http://localhost:8000/api/auth/firebase', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${idToken}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        firebase_uid: user.uid,
        email: user.email,
        display_name: user.displayName,
        photo_url: user.photoURL
      })
    });
    
    const data = await response.json();
    console.log('Backend user:', data.data);
    
    // 4. Store user data in frontend state
    // Store idToken for future requests
    
  } catch (error) {
    console.error('Sign-in error:', error);
  }
}
```

### Making Authenticated Requests

```typescript
// For any authenticated API request
const idToken = await auth.currentUser?.getIdToken();

fetch('http://localhost:8000/api/auth/me', {
  headers: {
    'Authorization': `Bearer ${idToken}`
  }
});
```

---

## Troubleshooting

### Error: "Firebase service account key not found"
**Solution:** Download `serviceAccountKey.json` from Firebase Console and place in project root.

### Error: "firebase-admin not installed"
**Solution:** Run `pip install firebase-admin==6.2.0`

### Error: "Invalid Firebase token"
**Solution:** 
- Make sure you're sending the ID token, not the refresh token
- Token expires after 1 hour - get a fresh token with `user.getIdToken(true)`
- Verify the token is sent in `Authorization: Bearer <token>` format

### Error: "Firebase UID mismatch"
**Solution:** The `firebase_uid` in request body must match the UID in the Firebase token.

### Error: "User not found"
**Solution:** User must exist in database first. For new users, contact admin to create account, or modify the endpoint to auto-create users.

---

## Database Migration Already Applied

✅ The following SQL has already been executed on your database:

```sql
ALTER TABLE "User" 
ADD COLUMN IF NOT EXISTS firebase_uid VARCHAR(255) UNIQUE,
ADD COLUMN IF NOT EXISTS email VARCHAR(255),
ADD COLUMN IF NOT EXISTS display_name VARCHAR(255),
ADD COLUMN IF NOT EXISTS photo_url TEXT,
ADD COLUMN IF NOT EXISTS registration_number VARCHAR(50),
ADD COLUMN IF NOT EXISTS provider VARCHAR(50) DEFAULT 'google',
ADD COLUMN IF NOT EXISTS last_login_at TIMESTAMP,
ADD COLUMN IF NOT EXISTS created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;

CREATE INDEX IF NOT EXISTS idx_user_firebase_uid ON "User"(firebase_uid);
CREATE INDEX IF NOT EXISTS idx_user_email ON "User"(email);
```

---

## Security Best Practices

✅ **Implemented:**
- Firebase ID token verification on every request
- UID validation between token and request body
- HTTPS recommended for production
- Service account key not in version control

⚠️ **TODO for Production:**
- Add rate limiting to auth endpoints
- Implement CORS with specific origins only
- Use environment variables for all secrets
- Add logging for failed authentication attempts
- Implement token refresh logic on frontend
- Add user role-based access control (RBAC)

---

## Next Steps

1. ✅ Download `serviceAccountKey.json` from Firebase Console
2. ✅ Place it in project root
3. ✅ Restart the backend server
4. ✅ Test the `/api/auth/firebase` endpoint
5. ⏳ Update frontend to call backend after Firebase sign-in
6. ⏳ Store Firebase ID token in frontend (localStorage/cookie)
7. ⏳ Include token in all authenticated API requests

---

## Contact & Support

If you encounter any issues:
1. Check the terminal output for Firebase initialization messages
2. Verify `serviceAccountKey.json` is in the correct location
3. Test with Swagger UI at http://localhost:8000/docs
4. Check Firebase Console for authentication logs

**Status:** ✅ Backend ready for Firebase authentication!
