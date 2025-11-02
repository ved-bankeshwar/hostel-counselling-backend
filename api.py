from fastapi import FastAPI, HTTPException, Body, status, Header, Depends
from pydantic import BaseModel, Field
from typing import Optional, List
from dbconfig import (
    counselling_session, 
    queue_management, 
    roommate_approval, 
    preference, 
    room_lock,
    friendship,
    user,
    hostel,
    block,
    floor,
    room,
    room_assignment
)
from firebase_auth import router as firebase_auth_router, verify_firebase_token
from friend_requests import router as friend_requests_router, get_user_by_firebase_uid
from allocation import router as allocation_router

app = FastAPI(
    title="Hostel Room Counselling API",
    description="API for hostel room allocation system with dual-queue architecture and Firebase authentication",
    version="1.0.0"
)

# Include routers
app.include_router(firebase_auth_router)
app.include_router(friend_requests_router)
app.include_router(allocation_router)

# ==================== Pydantic Models ====================

# Friendship Models
class FriendshipRequest(BaseModel):
    userId: int = Field(..., description="User sending the request")
    friendId: int = Field(..., description="User receiving the request")

class FriendshipStatusUpdate(BaseModel):
    status: str = Field(..., description="Status: pending, accepted, rejected")

# Preference Models
class PreferenceCreate(BaseModel):
    user_id: int = Field(..., description="User ID")
    session_id: int = Field(..., description="Counselling session ID")
    room_id: int = Field(..., description="Preferred room ID")
    priority: int = Field(..., description="Priority order (1 = highest)")
    roommate_user_ids: Optional[List[int]] = Field(default=None, description="Preferred roommates")

class PreferenceUpdate(BaseModel):
    room_id: Optional[int] = Field(None, description="Preferred room ID")
    priority: Optional[int] = Field(None, description="Priority order")
    roommate_user_ids: Optional[List[int]] = Field(None, description="Preferred roommates")

# Approval Models
class ApprovalRequest(BaseModel):
    requester_user_id: int = Field(..., description="User requesting approval")
    approver_user_id: int = Field(..., description="User who needs to approve")
    session_id: int = Field(..., description="Counselling session ID")
    room_id: int = Field(..., description="Room ID for approval")

# ==================== Hostel Structure Endpoints ====================

@app.get("/api/hostels", tags=["Hostel"])
def get_all_hostels():
    """Get all hostels"""
    try:
        result = hostel.get_all_hostels()
        return {"success": True, "data": result, "count": len(result)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/hostels/{hostel_id}", tags=["Hostel"])
def get_hostel_by_id(hostel_id: int):
    """Get hostel details by ID"""
    try:
        result = hostel.get_hostel_by_id(hostel_id)
        if not result:
            raise HTTPException(status_code=404, detail="Hostel not found")
        return {"success": True, "data": result}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/hostels/{hostel_id}/blocks", tags=["Hostel"])
def get_hostel_blocks(hostel_id: int):
    """Get all blocks in a hostel"""
    try:
        result = block.get_blocks_by_hostel_id(hostel_id)
        return {"success": True, "data": result, "count": len(result)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/blocks/{block_id}", tags=["Block"])
def get_block_by_id(block_id: int):
    """Get block details by ID"""
    try:
        result = block.get_block_by_id(block_id)
        if not result:
            raise HTTPException(status_code=404, detail="Block not found")
        return {"success": True, "data": result}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/blocks/{block_id}/floors", tags=["Block"])
def get_block_floors(block_id: int):
    """Get all floors in a block"""
    try:
        result = floor.get_floors_by_block_id(block_id)
        return {"success": True, "data": result, "count": len(result)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/floors/{floor_id}", tags=["Floor"])
def get_floor_by_id(floor_id: int):
    """Get floor details by ID"""
    try:
        result = floor.get_floor_by_id(floor_id)
        if not result:
            raise HTTPException(status_code=404, detail="Floor not found")
        return {"success": True, "data": result}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/floors/{floor_id}/rooms", tags=["Floor"])
def get_floor_rooms(floor_id: int):
    """Get all rooms on a floor"""
    try:
        result = room.get_rooms_by_floor_id(floor_id)
        return {"success": True, "data": result, "count": len(result)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/rooms/available", tags=["Room"])
def get_available_rooms():
    """Get all available rooms with optional filters"""
    try:
        all_rooms = room.get_all_rooms()
        # Filter for available rooms (is_available = True)
        available = [r for r in all_rooms if r.get('isAvailable', False) or r.get('is_available', False)]
        return {"success": True, "data": available, "count": len(available)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/rooms/{room_id}", tags=["Room"])
def get_room_by_id(room_id: int):
    """Get room details by ID"""
    try:
        result = room.get_room_by_id(room_id)
        if not result:
            raise HTTPException(status_code=404, detail="Room not found")
        return {"success": True, "data": result}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== Session Management Endpoints ====================

@app.get("/api/session/current", tags=["Session"])
def get_current_session():
    """Get the current active counselling session"""
    try:
        result = counselling_session.get_active_session()
        if not result:
            raise HTTPException(status_code=404, detail="No active session found")
        return {"success": True, "data": result}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/session/{session_id}", tags=["Session"])
def get_session_by_id(session_id: int):
    """Get session details by ID"""
    try:
        result = counselling_session.get_session_by_id(session_id)
        if not result:
            raise HTTPException(status_code=404, detail="Session not found")
        return {"success": True, "data": result}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== Preference Management Endpoints ====================

@app.get("/api/preferences/{user_id}", tags=["Preference"])
def get_user_preferences(user_id: int):
    """Get all preferences for a user"""
    try:
        result = preference.get_preferences_by_user_id(user_id)
        return {"success": True, "data": result, "count": len(result)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/preferences", tags=["Preference"])
def create_preference_endpoint(pref: PreferenceCreate):
    """Create a new preference"""
    try:
        result = preference.create_preference(pref.dict())
        return {"success": True, "message": "Preference created", "data": result}
    except Exception as e:
        if "duplicate key" in str(e).lower() or "unique" in str(e).lower():
            raise HTTPException(status_code=400, detail="Preference already exists")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/preferences/{preference_id}", tags=["Preference"])
def update_preference_endpoint(preference_id: int, pref: PreferenceUpdate):
    """Update a preference"""
    try:
        update_data = {k: v for k, v in pref.dict().items() if v is not None}
        result = preference.update_preference(preference_id, update_data)
        if not result:
            raise HTTPException(status_code=404, detail="Preference not found")
        return {"success": True, "message": "Preference updated", "data": result}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/preferences/{preference_id}", tags=["Preference"])
def delete_preference_endpoint(preference_id: int):
    """Delete a preference"""
    try:
        result = preference.delete_preference(preference_id)
        if not result:
            raise HTTPException(status_code=404, detail="Preference not found")
        return {"success": True, "message": "Preference deleted", "data": result}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/preferences/lock", tags=["Preference"])
async def lock_user_preferences(token_data: dict = Depends(verify_firebase_token)):
    """Lock all preferences for the current user"""
    try:
        from dbconfig.user import get_connection
        from psycopg2.extras import RealDictCursor
        
        conn = get_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Get user ID from firebase UID
        cursor.execute('SELECT id FROM "User" WHERE "firebaseUid" = %s', (token_data["uid"],))
        user = cursor.fetchone()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        user_id = user["id"]
        
        # Update all preferences for this user to locked status
        cursor.execute(
            """UPDATE "Preference" SET "isLocked" = true WHERE "userId" = %s RETURNING *""",
            (user_id,)
        )
        
        locked_preferences = cursor.fetchall()
        conn.commit()
        cursor.close()
        conn.close()
        
        return {
            "success": True,
            "message": "Preferences locked successfully",
            "data": [dict(p) for p in locked_preferences],
            "count": len(locked_preferences)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to lock preferences: {str(e)}")
# ==================== Roommate Approval Management Endpoints ====================

@app.get("/api/approvals/{user_id}", tags=["Approval"])
def get_user_approvals(user_id: int):
    """Get all approvals for a user (simplified version)"""
    try:
        # Query the database directly with corrected SQL
        import psycopg2
        from psycopg2.extras import RealDictCursor
        
        conn = psycopg2.connect(
            host='localhost',
            port=5432,
            database='room_counselling',
            user='admin',
            password='admin123'
        )
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Get requests where user is the requester
        cursor.execute(
            'SELECT * FROM "RoommateApproval" WHERE "requesterId" = %s ORDER BY "requestedAt" DESC',
            (user_id,)
        )
        sent = [dict(row) for row in cursor.fetchall()]
        
        # Get requests where user is the approver
        cursor.execute(
            'SELECT * FROM "RoommateApproval" WHERE "approverId" = %s ORDER BY "requestedAt" DESC',
            (user_id,)
        )
        received = [dict(row) for row in cursor.fetchall()]
        
        cursor.close()
        conn.close()
        
        return {"success": True, "data": {"sent": sent, "received": received}, "count": len(sent) + len(received)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/approvals/{user_id}/pending", tags=["Approval"])
def get_pending_approvals_endpoint(user_id: int):
    """Get pending approvals for a user"""
    try:
        # Query the database directly with corrected SQL
        import psycopg2
        from psycopg2.extras import RealDictCursor
        
        conn = psycopg2.connect(
            host='localhost',
            port=5432,
            database='room_counselling',
            user='admin',
            password='admin123'
        )
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        cursor.execute(
            'SELECT * FROM "RoommateApproval" WHERE "approverId" = %s AND status = \'pending\' ORDER BY "requestedAt" DESC',
            (user_id,)
        )
        result = [dict(row) for row in cursor.fetchall()]
        
        cursor.close()
        conn.close()
        
        return {"success": True, "data": result, "count": len(result)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/approvals", tags=["Approval"])
def send_approval_request_endpoint(approval: ApprovalRequest):
    """Send a roommate approval request"""
    try:
        result = roommate_approval.create_approval(approval.dict())
        return {"success": True, "message": "Approval request sent", "data": result}
    except Exception as e:
        if "duplicate key" in str(e).lower() or "unique" in str(e).lower():
            raise HTTPException(status_code=400, detail="Approval request already exists")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/approvals/{approval_id}/approve", tags=["Approval"])
def approve_request_endpoint(approval_id: int):
    """Approve a roommate request"""
    try:
        result = roommate_approval.update_approval_status(approval_id, {"status": "approved"})
        if not result:
            raise HTTPException(status_code=404, detail="Approval not found")
        return {"success": True, "message": "Request approved", "data": result}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/approvals/{approval_id}/reject", tags=["Approval"])
def reject_request_endpoint(approval_id: int):
    """Reject a roommate request"""
    try:
        result = roommate_approval.update_approval_status(approval_id, {"status": "rejected"})
        if not result:
            raise HTTPException(status_code=404, detail="Approval not found")
        return {"success": True, "message": "Request rejected", "data": result}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== Room Assignment Endpoints ====================

@app.get("/api/assignments/{user_id}", tags=["Assignment"])
def get_user_assignment(user_id: int):
    """Get room assignment for a user"""
    try:
        result = room_assignment.get_room_assignments_by_user_id(user_id)
        if not result or len(result) == 0:
            raise HTTPException(status_code=404, detail="No assignment found for user")
        return {"success": True, "data": result[0] if len(result) == 1 else result}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/assignments/room/{room_id}", tags=["Assignment"])
def get_room_assignments(room_id: int):
    """Get all assignments for a room"""
    try:
        result = room_assignment.get_room_assignments_by_room_id(room_id)
        return {"success": True, "data": result, "count": len(result)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== Queue Status Endpoints ====================

@app.get("/api/queue/turn/{user_id}", tags=["Queue"])
def get_turn_position(user_id: int):
    """Get turn queue position for a user"""
    try:
        result = queue_management.get_turn_by_user_id(user_id)
        if not result:
            raise HTTPException(status_code=404, detail="User not in turn queue")
        return {"success": True, "data": result}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/queue/processing/{user_id}", tags=["Queue"])
def get_processing_status_endpoint(user_id: int):
    """Get processing queue status for a user"""
    try:
        # Get processing queue status (simplified - returns overall status)
        # In a real implementation, you'd have a function to get by user_id
        result = queue_management.get_processing_queue_status()
        return {"success": True, "data": result, "message": "Overall queue status - user-specific status not yet implemented"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== Friendship Management Endpoints ====================

@app.get("/api/friends/{user_id}", tags=["Friendship"])
def get_user_friends(user_id: int):
    """Get all friends for a user (both sent and received friendships)"""
    try:
        friendships = friendship.get_friendships_by_user_id(user_id)
        return {"success": True, "data": friendships, "count": len(friendships)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/friends/{user_id}/accepted", tags=["Friendship"])
def get_accepted_friends(user_id: int):
    """Get only accepted friends for a user"""
    try:
        friends = friendship.get_accepted_friends(user_id)
        return {"success": True, "data": friends, "count": len(friends)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/friends/{user_id}/requests", tags=["Friendship"])
def get_friend_requests(user_id: int):
    """Get pending friend requests for a user"""
    try:
        all_friendships = friendship.get_friendships_by_user_id(user_id)
        # Filter for pending requests where user is the recipient (friendId)
        pending_requests = [f for f in all_friendships if f['status'] == 'pending' and f['friendId'] == user_id]
        return {"success": True, "data": pending_requests, "count": len(pending_requests)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/friends/request", tags=["Friendship"])
def send_friend_request(request: FriendshipRequest):
    """Send a friend request"""
    try:
        # Validate that users are different
        if request.userId == request.friendId:
            raise HTTPException(status_code=400, detail="Cannot send friend request to yourself")
        
        # Create friendship with pending status
        data = {
            "userId": request.userId,
            "friendId": request.friendId,
            "status": "pending"
        }
        result = friendship.create_friendship(data)
        return {"success": True, "message": "Friend request sent", "data": result}
    except Exception as e:
        if "duplicate key" in str(e).lower() or "unique" in str(e).lower():
            raise HTTPException(status_code=400, detail="Friend request already exists")
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/api/friends/{friendship_id}/accept", tags=["Friendship"])
def accept_friend_request(friendship_id: int):
    """Accept a friend request"""
    try:
        # Update status to accepted
        updated = friendship.update_friendship(friendship_id, {"status": "accepted"})
        if not updated:
            raise HTTPException(status_code=404, detail="Friendship not found")
        return {"success": True, "message": "Friend request accepted", "data": updated}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/api/friends/{friendship_id}/reject", tags=["Friendship"])
def reject_friend_request(friendship_id: int):
    """Reject a friend request"""
    try:
        # Update status to rejected
        updated = friendship.update_friendship(friendship_id, {"status": "rejected"})
        if not updated:
            raise HTTPException(status_code=404, detail="Friendship not found")
        return {"success": True, "message": "Friend request rejected", "data": updated}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/friends/{friendship_id}", tags=["Friendship"])
def remove_friend(friendship_id: int):
    """Remove a friend or cancel a friend request"""
    try:
        deleted = friendship.delete_friendship(friendship_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Friendship not found")
        return {"success": True, "message": "Friendship removed", "data": deleted}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== Counselling Session Endpoints ====================

def create_counselling_session(data: dict = Body(...)):
    # Expecting {"name": ..., "turn_duration": ...}
    name = data.get("name")
    turn_duration = data.get("turn_duration", 30)
    if not name:
        return {"error": "Missing session name"}
    return counselling_session.create_session(name, turn_duration)

@app.post("/counselling-session/{session_id}/start")
def start_counselling_session(session_id: int):
    return counselling_session.start_session(session_id)

@app.post("/counselling-session/{session_id}/pause")
def pause_counselling_session(session_id: int):
    return counselling_session.pause_session(session_id)

@app.post("/counselling-session/{session_id}/resume")
def resume_counselling_session(session_id: int):
    return counselling_session.resume_session(session_id)

@app.get("/counselling-session/current")
def get_current_counselling_session():
    return counselling_session.get_active_session()

@app.patch("/counselling-session/{session_id}/rank")
def update_counselling_session_rank(session_id: int, data: dict = Body(...)):
    # Expecting {"rank": ..., "user_id": ...}
    rank = data.get("rank")
    user_id = data.get("user_id")
    if rank is None:
        return {"error": "Missing rank"}
    return counselling_session.update_current_rank(session_id, rank, user_id)


@app.get("/counselling-session/{session_id}/turn-info")
def get_counselling_turn_info(session_id: int):
    """Expose current turn information (including remaining seconds) for a session."""
    try:
        info = counselling_session.get_current_turn_info(session_id)
        if not info:
            raise HTTPException(status_code=404, detail="Session or turn info not found")
        return {"success": True, "data": info}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/counselling/{session_id}/is-my-turn")
async def is_my_turn(session_id: int, authorization: str = Header(None)):
    """Check if the authenticated user currently has the turn for the given session.

    Returns remaining seconds and a boolean `isMyTurn`.
    """
    try:
        # Verify Firebase token and map to user
        decoded = await verify_firebase_token(authorization)
        current_user = get_user_by_firebase_uid(decoded['uid'])
        if not current_user:
            raise HTTPException(status_code=404, detail="User not found")

        info = counselling_session.get_current_turn_info(session_id)
        if not info:
            return {"success": True, "isMyTurn": False, "message": "No active turn info"}

        is_my_turn = False
        # Prefer explicit currentUserId if set, otherwise compare ranks
        if info.get('currentUserId'):
            is_my_turn = (info.get('currentUserId') == current_user['id'])
        else:
            is_my_turn = (info.get('currentRank') == current_user.get('rank'))

        return {
            "success": True,
            "isMyTurn": is_my_turn,
            "remainingSeconds": info.get('remainingSeconds'),
            "currentRank": info.get('currentRank'),
            "currentUserId": info.get('currentUserId')
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Queue Management Endpoints
@app.post("/queue/turn")
def add_to_turn_queue(data: dict):
    return queue_management.add_to_turn_queue(data)

@app.get("/queue/turn/{user_id}/position")
def get_turn_queue_position(user_id: int):
    return queue_management.get_turn_queue_position(user_id)

@app.patch("/queue/turn/{user_id}/status")
def update_turn_queue_status(user_id: int, status: str):
    return queue_management.update_turn_queue_status(user_id, status)

@app.delete("/queue/turn/{user_id}")
def remove_from_turn_queue(user_id: int):
    return queue_management.remove_from_turn_queue(user_id)

@app.post("/queue/processing")
def add_to_processing_queue(data: dict):
    return queue_management.add_to_processing_queue(data)

@app.get("/queue/processing/{user_id}/position")
def get_processing_queue_position(user_id: int):
    return queue_management.get_processing_queue_position(user_id)

@app.patch("/queue/processing/{user_id}/status")
def update_processing_queue_status(user_id: int, status: str):
    return queue_management.update_processing_queue_status(user_id, status)

@app.delete("/queue/processing/{user_id}")
def remove_from_processing_queue(user_id: int):
    return queue_management.remove_from_processing_queue(user_id)

# RoommateApproval Endpoints
@app.post("/roommate-approval/")
def send_roommate_approval(data: dict):
    return roommate_approval.send_approval(data)

@app.post("/roommate-approval/{approval_id}/accept")
def accept_roommate_approval(approval_id: int):
    return roommate_approval.accept_approval(approval_id)

@app.post("/roommate-approval/{approval_id}/reject")
def reject_roommate_approval(approval_id: int):
    return roommate_approval.reject_approval(approval_id)

@app.get("/roommate-approval/{user_id}/status")
def check_roommate_approval_status(user_id: int):
    return roommate_approval.check_approval_status(user_id)

@app.get("/roommate-approval/{user_id}/pending")
def get_pending_roommate_approvals(user_id: int):
    return roommate_approval.get_pending_approvals(user_id)

# Preference Endpoints
@app.post("/preference/")
def create_preference(data: dict):
    return preference.create_preference(data)

@app.patch("/preference/{preference_id}")
def update_preference(preference_id: int, data: dict):
    return preference.update_preference(preference_id, data)

@app.get("/preference/{user_id}")
def get_user_preference(user_id: int):
    return preference.get_user_preference(user_id)

# RoomLock Endpoints
@app.post("/room-lock/")
def lock_room(data: dict):
    return room_lock.lock_room(data)

@app.post("/room-lock/{lock_id}/unlock")
def unlock_room(lock_id: int):
    return room_lock.unlock_room(lock_id)

@app.get("/room-lock/{room_id}/status")
def check_room_lock_status(room_id: int):
    return room_lock.check_lock_status(room_id)

@app.delete("/room-lock/{lock_id}")
def remove_room_lock(lock_id: int):
    return room_lock.remove_lock(lock_id)


# ==================== TEST ENDPOINT (REMOVE IN PRODUCTION) ====================
# This endpoint bypasses Firebase authentication for development testing only
# ⚠️ REMOVE THIS BEFORE DEPLOYING TO PRODUCTION!

class TestLoginRequest(BaseModel):
    email: str = Field(..., description="Email of the user")

@app.post("/api/auth/test-login", tags=["auth"], deprecated=True)
async def test_login_no_firebase(request: TestLoginRequest):
    """
    TEST ONLY - Login without Firebase token.
    This endpoint bypasses Firebase authentication for testing.
    
    ⚠️ REMOVE THIS BEFORE DEPLOYING TO PRODUCTION!
    """
    from dbconfig.user import get_connection
    from psycopg2.extras import RealDictCursor
    from datetime import datetime
    
    conn = get_connection()
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute('SELECT * FROM "User" WHERE email = %s', (request.email,))
        user = cursor.fetchone()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Update last login
        cursor.execute(
            'UPDATE "User" SET "lastLoginAt" = %s WHERE email = %s RETURNING *',
            (datetime.utcnow(), request.email)
        )
        user = dict(cursor.fetchone())
        conn.commit()
        cursor.close()
        
        return {
            "success": True,
            "data": user,
            "message": "⚠️ TEST LOGIN - No authentication required",
            "warning": "This endpoint should be removed in production"
        }
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        conn.close()

