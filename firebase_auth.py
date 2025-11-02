import os
import firebase_admin
from firebase_admin import credentials, auth as firebase_auth
from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel
from dbconfig.user import get_connection
from datetime import datetime
from psycopg2.extras import RealDictCursor

router = APIRouter(prefix="/api/auth", tags=["auth"])

# Initialize Firebase Admin SDK
service_account_path = os.getenv("FIREBASE_SERVICE_ACCOUNT_PATH", "serviceAccountKey.json")

try:
    firebase_admin.get_app()
    print("[OK] Firebase Admin SDK already initialized")
except ValueError:
    try:
        cred = credentials.Certificate(service_account_path)
        firebase_admin.initialize_app(cred)
        print(f"[OK] Firebase Admin SDK initialized from {service_account_path}")
    except Exception as e:
        print(f"[ERROR] Firebase Admin SDK initialization failed: {e}")

# Pydantic models
class FirebaseLoginRequest(BaseModel):
    firebaseUid: str
    email: str
    displayName: str
    photoUrl: str = None

class UserUpdateRequest(BaseModel):
    registrationNumber: str = None
    displayName: str = None

# Helper function to verify Firebase token
async def verify_firebase_token(authorization: str = Header(None)):
    # Enhanced logging for debugging
    print(f"[AUTH] Authorization header: {authorization[:50] if authorization else 'None'}...")
    
    if not authorization:
        print("[AUTH] ❌ No authorization header")
        raise HTTPException(status_code=401, detail="No authorization header")
    
    if not authorization.startswith("Bearer "):
        print(f"[AUTH] ❌ Invalid format: {authorization[:20]}")
        raise HTTPException(status_code=401, detail="Invalid authorization header format")
    
    token = authorization.replace("Bearer ", "")
    print(f"[AUTH] Token length: {len(token)} characters")
    
    try:
        decoded_token = firebase_auth.verify_id_token(token)
        print(f"[AUTH] OK - Token verified for UID: {decoded_token['uid']}, Email: {decoded_token.get('email', 'N/A')}")
        return decoded_token
    except firebase_auth.ExpiredIdTokenError:
        print("[AUTH] ERROR - Token expired")
        raise HTTPException(status_code=401, detail="Token expired")
    except firebase_auth.InvalidIdTokenError as e:
        print(f"[AUTH] ERROR - Invalid token: {str(e)}")
        raise HTTPException(status_code=401, detail=f"Invalid Firebase ID token: {str(e)}")
    except Exception as e:
        print(f"[AUTH] ERROR - Verification failed: {str(e)}")
        raise HTTPException(status_code=401, detail=f"Token verification failed: {str(e)}")

# Endpoints
@router.post("/firebase")
async def firebase_login(request: FirebaseLoginRequest, authorization: str = Header(None)):
    token_data = await verify_firebase_token(authorization)
    
    if token_data["uid"] != request.firebaseUid:
        raise HTTPException(status_code=403, detail="Firebase UID mismatch")
    
    conn = get_connection()
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute('SELECT * FROM "User" WHERE "firebaseUid" = %s', (request.firebaseUid,))
        user = cursor.fetchone()
        
        if user:
            cursor.execute(
                '''UPDATE "User" SET email = %s, "displayName" = %s, "lastLoginAt" = %s WHERE "firebaseUid" = %s RETURNING *''',
                (request.email, request.displayName, datetime.utcnow(), request.firebaseUid)
            )
            user = dict(cursor.fetchone())
        else:
            # For new users, we need to set default values for required fields
            # These can be updated later via the profile update endpoint
            cursor.execute(
                '''INSERT INTO "User" ("firebaseUid", email, "displayName", gender, rank, hostel, "lastLoginAt", "createdAt") 
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING *''',
                (request.firebaseUid, request.email, request.displayName, 
                 'other', 999999, 'other', datetime.utcnow(), datetime.utcnow())
            )
            user = dict(cursor.fetchone())
        
        conn.commit()
        cursor.close()
        return {"success": True, "data": user, "message": "User logged in successfully"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        conn.close()

@router.get("/me")
async def get_current_user(authorization: str = Header(None)):
    token_data = await verify_firebase_token(authorization)
    conn = get_connection()
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute('SELECT * FROM "User" WHERE "firebaseUid" = %s', (token_data["uid"],))
        user = cursor.fetchone()
        cursor.close()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return dict(user)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        conn.close()

@router.patch("/me")
async def update_user_profile(updates: UserUpdateRequest, authorization: str = Header(None)):
    token_data = await verify_firebase_token(authorization)
    conn = get_connection()
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        set_clauses = []
        params = []
        if updates.registrationNumber is not None:
            set_clauses.append('"registrationNumber" = %s')
            params.append(updates.registrationNumber)
        if updates.displayName is not None:
            set_clauses.append('"displayName" = %s')
            params.append(updates.displayName)
        if not set_clauses:
            raise HTTPException(status_code=400, detail="No fields to update")
        set_clauses.append('"updatedAt" = %s')
        params.append(datetime.utcnow())
        params.append(token_data["uid"])
        query = f'UPDATE "User" SET {", ".join(set_clauses)} WHERE "firebaseUid" = %s RETURNING *'
        cursor.execute(query, params)
        user = cursor.fetchone()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        conn.commit()
        cursor.close()
        return dict(user)
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        conn.close()

@router.get("/user/{firebase_uid}")
async def get_user_by_firebase_uid(firebase_uid: str):
    conn = get_connection()
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute('SELECT * FROM "User" WHERE "firebaseUid" = %s', (firebase_uid,))
        user = cursor.fetchone()
        cursor.close()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return dict(user)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        conn.close()