"""Friend Request API endpoints for the Hostel Counselling API."""

from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel
from typing import Optional, List
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
from firebase_auth import verify_firebase_token
from config import DB_CONFIG

router = APIRouter(prefix="/api", tags=["Friends"])


def get_connection():
    """Create and return a database connection."""
    return psycopg2.connect(**DB_CONFIG)


# Request/Response Models
class FriendRequestCreate(BaseModel):
    receiverRegistrationNumber: str


class UserBasicInfo(BaseModel):
    id: int
    email: str
    displayName: str
    registrationNumber: Optional[str]
    gender: str
    rank: int
    hostel: str
    isActive: bool


class FriendRequestResponse(BaseModel):
    id: int
    userId: int  # sender
    friendId: int  # receiver
    status: str
    createdAt: datetime
    sender: Optional[UserBasicInfo] = None
    receiver: Optional[UserBasicInfo] = None


class SuccessResponse(BaseModel):
    success: bool
    data: Optional[dict] = None
    message: Optional[str] = None


# Helper function to get user from database
def get_user_by_firebase_uid(firebase_uid: str):
    """Get user by Firebase UID"""
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        cursor.execute(
            'SELECT * FROM "User" WHERE "firebaseUid" = %s',
            (firebase_uid,)
        )
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        return user
    except Exception as e:
        cursor.close()
        conn.close()
        raise Exception(f"Database error: {str(e)}")


def get_user_by_registration_number(registration_number: str):
    """Get user by registration number"""
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        cursor.execute(
            'SELECT * FROM "User" WHERE "registrationNumber" = %s',
            (registration_number,)
        )
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        return user
    except Exception as e:
        cursor.close()
        conn.close()
        raise Exception(f"Database error: {str(e)}")


def get_user_by_id(user_id: int):
    """Get user by ID"""
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        cursor.execute(
            'SELECT * FROM "User" WHERE id = %s',
            (user_id,)
        )
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        return user
    except Exception as e:
        cursor.close()
        conn.close()
        raise Exception(f"Database error: {str(e)}")


# ENDPOINTS

@router.get("/users/verify/{registration_number}")
async def verify_user(
    registration_number: str,
    authorization: str = Header(None)
):
    """
    Verify that a user exists with the given registration number.
    
    **Headers:**
    - Authorization: Bearer <firebase_id_token>
    
    **Response:**
    Returns user details if found, 404 if not found.
    """
    # Verify Firebase token
    await verify_firebase_token(authorization)
    
    # Look up user by registration number
    user = get_user_by_registration_number(registration_number)
    
    if not user:
        raise HTTPException(
            status_code=404,
            detail=f"User not found with registration number: {registration_number}"
        )
    
    return {
        "success": True,
        "data": {
            "id": user['id'],
            "firebaseUid": user['firebaseUid'],
            "email": user['email'],
            "displayName": user['displayName'],
            "registrationNumber": user['registrationNumber'],
            "gender": user['gender'],
            "rank": user['rank'],
            "hostel": user['hostel'],
            "isActive": user['isActive'],
            "lastLoginAt": user['lastLoginAt'],
            "createdAt": user['createdAt']
        }
    }


@router.post("/friends/request", status_code=201)
async def send_friend_request(
    request: FriendRequestCreate,
    authorization: str = Header(None)
):
    """
    Send a friend request to another user by their registration number.
    
    **Headers:**
    - Authorization: Bearer <firebase_id_token>
    
    **Request Body:**
    - receiverRegistrationNumber: The registration number of the user to send request to
    
    **Response:**
    Returns the created friend request.
    """
    # Verify Firebase token and get current user
    decoded_token = await verify_firebase_token(authorization)
    current_user = get_user_by_firebase_uid(decoded_token['uid'])
    
    if not current_user:
        raise HTTPException(status_code=404, detail="Current user not found")
    
    # Find receiver by registration number
    receiver = get_user_by_registration_number(request.receiverRegistrationNumber)
    
    if not receiver:
        raise HTTPException(
            status_code=404,
            detail=f"User not found with registration number: {request.receiverRegistrationNumber}"
        )
    
    # Validate not sending to self
    if receiver['id'] == current_user['id']:
        raise HTTPException(
            status_code=400,
            detail="Cannot send friend request to yourself"
        )
    
    # Check for existing friendship (in either direction)
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        # Check if friendship already exists in either direction
        cursor.execute("""
            SELECT * FROM "Friendship" 
            WHERE ("userId" = %s AND "friendId" = %s) 
               OR ("userId" = %s AND "friendId" = %s)
        """, (current_user['id'], receiver['id'], receiver['id'], current_user['id']))
        
        existing = cursor.fetchone()
        
        if existing:
            if existing['status'] == 'pending':
                raise HTTPException(
                    status_code=400,
                    detail="Friend request already exists and is pending"
                )
            elif existing['status'] == 'accepted':
                raise HTTPException(
                    status_code=400,
                    detail="You are already friends with this user"
                )
            elif existing['status'] == 'rejected':
                # Allow resending after rejection
                cursor.execute("""
                    UPDATE "Friendship"
                    SET status = 'pending'::"FriendStatus", 
                        "createdAt" = CURRENT_TIMESTAMP
                    WHERE id = %s
                    RETURNING *
                """, (existing['id'],))
                
                friendship = cursor.fetchone()
                conn.commit()
        else:
            # Create new friend request
            cursor.execute("""
                INSERT INTO "Friendship" ("userId", "friendId", status)
                VALUES (%s, %s, 'pending'::"FriendStatus")
                RETURNING *
            """, (current_user['id'], receiver['id']))
            
            friendship = cursor.fetchone()
            conn.commit()
        
        cursor.close()
        conn.close()
        
        return {
            "success": True,
            "data": {
                "id": friendship['id'],
                "senderId": friendship['userId'],
                "receiverId": friendship['friendId'],
                "status": friendship['status'],
                "createdAt": friendship['createdAt']
            },
            "message": "Friend request sent successfully"
        }
        
    except HTTPException:
        cursor.close()
        conn.close()
        raise
    except Exception as e:
        conn.rollback()
        cursor.close()
        conn.close()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.get("/friends/requests/pending")
async def get_pending_requests(
    authorization: str = Header(None)
):
    """
    Get all pending friend requests where the current user is the receiver.
    
    **Headers:**
    - Authorization: Bearer <firebase_id_token>
    
    **Response:**
    Returns list of pending friend requests with sender details.
    """
    # Verify Firebase token and get current user
    decoded_token = await verify_firebase_token(authorization)
    current_user = get_user_by_firebase_uid(decoded_token['uid'])
    
    if not current_user:
        raise HTTPException(status_code=404, detail="Current user not found")
    
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        # Get pending friend requests where current user is the receiver
        cursor.execute("""
            SELECT f.*, 
                   u.id as sender_id,
                   u.email as sender_email,
                   u."displayName" as sender_name,
                   u."registrationNumber" as sender_reg,
                   u.gender as sender_gender,
                   u.rank as sender_rank,
                   u.hostel as sender_hostel,
                   u."isActive" as sender_active
            FROM "Friendship" f
            JOIN "User" u ON f."userId" = u.id
            WHERE f."friendId" = %s AND f.status = 'pending'
            ORDER BY f."createdAt" DESC
        """, (current_user['id'],))
        
        requests = cursor.fetchall()
        cursor.close()
        conn.close()
        
        # Format response
        formatted_requests = []
        for req in requests:
            formatted_requests.append({
                "id": req['id'],
                "senderId": req['userId'],
                "receiverId": req['friendId'],
                "status": req['status'],
                "createdAt": req['createdAt'],
                "sender": {
                    "id": req['sender_id'],
                    "email": req['sender_email'],
                    "displayName": req['sender_name'],
                    "registrationNumber": req['sender_reg'],
                    "gender": req['sender_gender'],
                    "rank": req['sender_rank'],
                    "hostel": req['sender_hostel'],
                    "isActive": req['sender_active']
                }
            })
        
        return {
            "success": True,
            "data": formatted_requests,
            "count": len(formatted_requests)
        }
        
    except Exception as e:
        cursor.close()
        conn.close()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.post("/friends/request/{request_id}/accept")
async def accept_friend_request(
    request_id: int,
    authorization: str = Header(None)
):
    """
    Accept a pending friend request.
    
    **Headers:**
    - Authorization: Bearer <firebase_id_token>
    
    **Parameters:**
    - request_id: ID of the friend request to accept
    
    **Response:**
    Returns the updated friend request.
    """
    # Verify Firebase token and get current user
    decoded_token = await verify_firebase_token(authorization)
    current_user = get_user_by_firebase_uid(decoded_token['uid'])
    
    if not current_user:
        raise HTTPException(status_code=404, detail="Current user not found")
    
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        # Get the friend request
        cursor.execute(
            'SELECT * FROM "Friendship" WHERE id = %s',
            (request_id,)
        )
        friend_request = cursor.fetchone()
        
        if not friend_request:
            raise HTTPException(status_code=404, detail="Friend request not found")
        
        # Validate current user is the receiver
        if friend_request['friendId'] != current_user['id']:
            raise HTTPException(
                status_code=403,
                detail="You are not authorized to accept this friend request"
            )
        
        # Validate status is pending
        if friend_request['status'] != 'pending':
            raise HTTPException(
                status_code=400,
                detail=f"Friend request is not pending (current status: {friend_request['status']})"
            )
        
        # Update status to accepted
        cursor.execute("""
            UPDATE "Friendship"
            SET status = 'accepted'::"FriendStatus"
            WHERE id = %s
            RETURNING *
        """, (request_id,))
        
        updated_request = cursor.fetchone()
        conn.commit()
        cursor.close()
        conn.close()
        
        return {
            "success": True,
            "data": {
                "id": updated_request['id'],
                "senderId": updated_request['userId'],
                "receiverId": updated_request['friendId'],
                "status": updated_request['status'],
                "createdAt": updated_request['createdAt']
            },
            "message": "Friend request accepted"
        }
        
    except HTTPException:
        cursor.close()
        conn.close()
        raise
    except Exception as e:
        conn.rollback()
        cursor.close()
        conn.close()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.post("/friends/request/{request_id}/reject")
async def reject_friend_request(
    request_id: int,
    authorization: str = Header(None)
):
    """
    Reject a pending friend request.
    
    **Headers:**
    - Authorization: Bearer <firebase_id_token>
    
    **Parameters:**
    - request_id: ID of the friend request to reject
    
    **Response:**
    Returns the updated friend request.
    """
    # Verify Firebase token and get current user
    decoded_token = await verify_firebase_token(authorization)
    current_user = get_user_by_firebase_uid(decoded_token['uid'])
    
    if not current_user:
        raise HTTPException(status_code=404, detail="Current user not found")
    
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        # Get the friend request
        cursor.execute(
            'SELECT * FROM "Friendship" WHERE id = %s',
            (request_id,)
        )
        friend_request = cursor.fetchone()
        
        if not friend_request:
            raise HTTPException(status_code=404, detail="Friend request not found")
        
        # Validate current user is the receiver
        if friend_request['friendId'] != current_user['id']:
            raise HTTPException(
                status_code=403,
                detail="You are not authorized to reject this friend request"
            )
        
        # Validate status is pending
        if friend_request['status'] != 'pending':
            raise HTTPException(
                status_code=400,
                detail=f"Friend request is not pending (current status: {friend_request['status']})"
            )
        
        # Update status to rejected
        cursor.execute("""
            UPDATE "Friendship"
            SET status = 'rejected'::"FriendStatus"
            WHERE id = %s
            RETURNING *
        """, (request_id,))
        
        updated_request = cursor.fetchone()
        conn.commit()
        cursor.close()
        conn.close()
        
        return {
            "success": True,
            "data": {
                "id": updated_request['id'],
                "senderId": updated_request['userId'],
                "receiverId": updated_request['friendId'],
                "status": updated_request['status'],
                "createdAt": updated_request['createdAt']
            },
            "message": "Friend request rejected"
        }
        
    except HTTPException:
        cursor.close()
        conn.close()
        raise
    except Exception as e:
        conn.rollback()
        cursor.close()
        conn.close()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.get("/friends")
async def get_friends_list(
    authorization: str = Header(None)
):
    """
    Get list of accepted friends for the current user.
    
    **Headers:**
    - Authorization: Bearer <firebase_id_token>
    
    **Response:**
    Returns list of friends (users with accepted friend requests).
    """
    # Verify Firebase token and get current user
    decoded_token = await verify_firebase_token(authorization)
    current_user = get_user_by_firebase_uid(decoded_token['uid'])
    
    if not current_user:
        raise HTTPException(status_code=404, detail="Current user not found")
    
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        # Get accepted friendships where current user is either sender or receiver
        cursor.execute("""
            SELECT DISTINCT
                CASE 
                    WHEN f."userId" = %s THEN f."friendId"
                    ELSE f."userId"
                END as friend_id
            FROM "Friendship" f
            WHERE (f."userId" = %s OR f."friendId" = %s)
              AND f.status = 'accepted'
        """, (current_user['id'], current_user['id'], current_user['id']))
        
        friend_ids = [row['friend_id'] for row in cursor.fetchall()]
        
        if not friend_ids:
            cursor.close()
            conn.close()
            return {
                "success": True,
                "data": [],
                "count": 0
            }
        
        # Get friend user details
        placeholders = ','.join(['%s'] * len(friend_ids))
        cursor.execute(f"""
            SELECT id, email, "displayName", "registrationNumber", 
                   gender, rank, hostel, "isActive"
            FROM "User"
            WHERE id IN ({placeholders})
        """, friend_ids)
        
        friends = cursor.fetchall()
        cursor.close()
        conn.close()
        
        # Format response
        formatted_friends = []
        for friend in friends:
            formatted_friends.append({
                "id": friend['id'],
                "email": friend['email'],
                "displayName": friend['displayName'],
                "registrationNumber": friend['registrationNumber'],
                "gender": friend['gender'],
                "rank": friend['rank'],
                "hostel": friend['hostel'],
                "isActive": friend['isActive']
            })
        
        return {
            "success": True,
            "data": formatted_friends,
            "count": len(formatted_friends)
        }
        
    except Exception as e:
        cursor.close()
        conn.close()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.get("/friends/requests")
async def get_all_friend_requests(
    authorization: str = Header(None)
):
    """
    Get all friend requests (sent and received) for the current user.
    
    **Headers:**
    - Authorization: Bearer <firebase_id_token>
    
    **Response:**
    Returns list of all friend requests with user details.
    """
    # Verify Firebase token and get current user
    decoded_token = await verify_firebase_token(authorization)
    current_user = get_user_by_firebase_uid(decoded_token['uid'])
    
    if not current_user:
        raise HTTPException(status_code=404, detail="Current user not found")
    
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        # Get all friend requests where current user is sender or receiver
        cursor.execute("""
            SELECT f.*,
                   sender.id as sender_id,
                   sender.email as sender_email,
                   sender."displayName" as sender_name,
                   sender."registrationNumber" as sender_reg,
                   sender.gender as sender_gender,
                   sender.rank as sender_rank,
                   sender.hostel as sender_hostel,
                   receiver.id as receiver_id,
                   receiver.email as receiver_email,
                   receiver."displayName" as receiver_name,
                   receiver."registrationNumber" as receiver_reg,
                   receiver.gender as receiver_gender,
                   receiver.rank as receiver_rank,
                   receiver.hostel as receiver_hostel
            FROM "Friendship" f
            JOIN "User" sender ON f."userId" = sender.id
            JOIN "User" receiver ON f."friendId" = receiver.id
            WHERE f."userId" = %s OR f."friendId" = %s
            ORDER BY f."createdAt" DESC
        """, (current_user['id'], current_user['id']))
        
        requests = cursor.fetchall()
        cursor.close()
        conn.close()
        
        # Format response
        formatted_requests = []
        for req in requests:
            formatted_requests.append({
                "id": req['id'],
                "senderId": req['userId'],
                "receiverId": req['friendId'],
                "status": req['status'],
                "createdAt": req['createdAt'],
                "sender": {
                    "id": req['sender_id'],
                    "email": req['sender_email'],
                    "displayName": req['sender_name'],
                    "registrationNumber": req['sender_reg'],
                    "gender": req['sender_gender'],
                    "rank": req['sender_rank'],
                    "hostel": req['sender_hostel']
                },
                "receiver": {
                    "id": req['receiver_id'],
                    "email": req['receiver_email'],
                    "displayName": req['receiver_name'],
                    "registrationNumber": req['receiver_reg'],
                    "gender": req['receiver_gender'],
                    "rank": req['receiver_rank'],
                    "hostel": req['receiver_hostel']
                }
            })
        
        return {
            "success": True,
            "data": formatted_requests,
            "count": len(formatted_requests)
        }
        
    except Exception as e:
        cursor.close()
        conn.close()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
