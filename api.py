from fastapi import FastAPI, HTTPException, Body, status, Header, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List
import psycopg2
from psycopg2.extras import RealDictCursor
from dbconfig import (
    counselling_session, 
    queue_management, 
    preference, 
    friendship,
    user,
    room
)
from firebase_auth import router as firebase_auth_router, verify_firebase_token
from friend_requests import router as friend_requests_router, get_user_by_firebase_uid
from allocation import router as allocation_router
from dotenv import load_dotenv
import os

# Load environment variables from .env.local if it exists
load_dotenv(".env.local")

app = FastAPI(
    title="Hostel Room Counselling API",
    description="API for hostel room allocation system with dual-queue architecture and Firebase authentication",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Local development
        "http://localhost:5173",  # Vite local
        "https://hostel-counselling-frontend.vercel.app",  # Production (no trailing slash)
        "*"  # Allow all origins temporarily for testing
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
    """Get all hostels with room statistics"""
    try:
        result = room.get_all_hostels()
        return {"success": True, "data": result, "count": len(result)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/hostels/{hostel_name}", tags=["Hostel"])
def get_hostel_by_name(hostel_name: str):
    """Get hostel details by name with room statistics"""
    try:
        # Query aggregated hostel data from Rooms table
        conn = psycopg2.connect(**room.DB_CONFIG)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        query = """
            SELECT 
                "hostelName" as name,
                COUNT(*) as "totalRooms",
                SUM("capacity") as "totalCapacity",
                SUM("occupied") as "totalOccupied",
                SUM("capacity" - "occupied") as "availableSlots"
            FROM "Rooms"
            WHERE "hostelName" = %s
            GROUP BY "hostelName"
        """
        cursor.execute(query, (hostel_name,))
        result = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        if not result:
            raise HTTPException(status_code=404, detail="Hostel not found")
        return {"success": True, "data": dict(result)}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/hostels/{hostel_name}/blocks", tags=["Hostel"])
def get_hostel_blocks(hostel_name: str):
    """Get all blocks in a hostel with room statistics"""
    try:
        conn = psycopg2.connect(**room.DB_CONFIG)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        query = """
            SELECT 
                "blockName" as name,
                "hostelName",
                COUNT(*) as "totalRooms",
                SUM("capacity") as "totalCapacity",
                SUM("occupied") as "totalOccupied",
                SUM("capacity" - "occupied") as "availableSlots"
            FROM "Rooms"
            WHERE "hostelName" = %s
            GROUP BY "blockName", "hostelName"
            ORDER BY "blockName"
        """
        cursor.execute(query, (hostel_name,))
        result = [dict(row) for row in cursor.fetchall()]
        
        cursor.close()
        conn.close()
        
        return {"success": True, "data": result, "count": len(result)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/blocks", tags=["Block"])
def get_all_blocks(hostelName: Optional[str] = None):
    """Get all blocks, optionally filtered by hostel name"""
    try:
        if hostelName:
            # Use the helper function from room.py
            result = room.get_blocks_by_hostel(hostelName)
        else:
            # Return all blocks grouped by hostel
            conn = psycopg2.connect(**room.DB_CONFIG)
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            query = """
                SELECT DISTINCT 
                    "blockName" as name,
                    "hostelName",
                    COUNT(*) as room_count,
                    SUM("capacity") as total_capacity,
                    SUM("occupied") as total_occupied,
                    SUM("capacity" - "occupied") as available_slots
                FROM "Rooms"
                GROUP BY "blockName", "hostelName"
                ORDER BY "hostelName", "blockName"
            """
            cursor.execute(query)
            result = [dict(row) for row in cursor.fetchall()]
            
            cursor.close()
            conn.close()
        
        return {"success": True, "data": result, "count": len(result)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/blocks/{hostel_name}/{block_name}", tags=["Block"])
def get_block_details(hostel_name: str, block_name: str):
    """Get block details by hostel and block name"""
    try:
        conn = psycopg2.connect(**room.DB_CONFIG)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        query = """
            SELECT 
                "blockName" as name,
                "hostelName",
                COUNT(*) as "totalRooms",
                SUM("capacity") as "totalCapacity",
                SUM("occupied") as "totalOccupied",
                SUM("capacity" - "occupied") as "availableSlots"
            FROM "Rooms"
            WHERE "hostelName" = %s AND "blockName" = %s
            GROUP BY "blockName", "hostelName"
        """
        cursor.execute(query, (hostel_name, block_name))
        result = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        if not result:
            raise HTTPException(status_code=404, detail="Block not found")
        return {"success": True, "data": dict(result)}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/floors", tags=["Floor"])
def get_all_floors(hostelName: Optional[str] = None, blockName: Optional[str] = None):
    """Get all floors, optionally filtered by hostel and/or block"""
    try:
        if hostelName and blockName:
            # Use the helper function from room.py
            result = room.get_floors_by_hostel_and_block(hostelName, blockName)
        else:
            # Build dynamic query based on filters
            conn = psycopg2.connect(**room.DB_CONFIG)
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            query = """
                SELECT DISTINCT 
                    "floorNumber" as number,
                    "blockName",
                    "hostelName",
                    COUNT(*) as room_count,
                    SUM("capacity") as total_capacity,
                    SUM("occupied") as total_occupied,
                    SUM("capacity" - "occupied") as available_slots
                FROM "Rooms"
            """
            
            conditions = []
            params = []
            
            if hostelName:
                conditions.append('"hostelName" = %s')
                params.append(hostelName)
            if blockName:
                conditions.append('"blockName" = %s')
                params.append(blockName)
            
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
            
            query += """
                GROUP BY "floorNumber", "blockName", "hostelName"
                ORDER BY "hostelName", "blockName", "floorNumber"
            """
            
            cursor.execute(query, params)
            result = [dict(row) for row in cursor.fetchall()]
            
            cursor.close()
            conn.close()
        
        return {"success": True, "data": result, "count": len(result)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/blocks/{hostel_name}/{block_name}/floors", tags=["Block"])
def get_block_floors(hostel_name: str, block_name: str):
    """Get all floors in a block with room statistics"""
    try:
        conn = psycopg2.connect(**room.DB_CONFIG)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        query = """
            SELECT 
                "floorNumber" as number,
                "blockName",
                "hostelName",
                COUNT(*) as "totalRooms",
                SUM("capacity") as "totalCapacity",
                SUM("occupied") as "totalOccupied",
                SUM("capacity" - "occupied") as "availableSlots"
            FROM "Rooms"
            WHERE "hostelName" = %s AND "blockName" = %s
            GROUP BY "floorNumber", "blockName", "hostelName"
            ORDER BY "floorNumber"
        """
        cursor.execute(query, (hostel_name, block_name))
        result = [dict(row) for row in cursor.fetchall()]
        
        cursor.close()
        conn.close()
        
        return {"success": True, "data": result, "count": len(result)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/floors/{hostel_name}/{block_name}/{floor_number}", tags=["Floor"])
def get_floor_details(hostel_name: str, block_name: str, floor_number: int):
    """Get floor details by hostel, block, and floor number"""
    try:
        conn = psycopg2.connect(**room.DB_CONFIG)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        query = """
            SELECT 
                "floorNumber" as number,
                "blockName",
                "hostelName",
                COUNT(*) as "totalRooms",
                SUM("capacity") as "totalCapacity",
                SUM("occupied") as "totalOccupied",
                SUM("capacity" - "occupied") as "availableSlots"
            FROM "Rooms"
            WHERE "hostelName" = %s AND "blockName" = %s AND "floorNumber" = %s
            GROUP BY "floorNumber", "blockName", "hostelName"
        """
        cursor.execute(query, (hostel_name, block_name, floor_number))
        result = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        if not result:
            raise HTTPException(status_code=404, detail="Floor not found")
        return {"success": True, "data": dict(result)}
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
def get_available_rooms(
    hostelName: Optional[str] = None,
    blockName: Optional[str] = None,
    floorNumber: Optional[int] = None,
    isAC: Optional[bool] = None,
    isDeluxe: Optional[bool] = None,
    isApartment: Optional[bool] = None
):
    """Get all available rooms (where capacity > occupied) with optional filters"""
    try:
        # Build filters dict
        filters = {'available': True, 'isLocked': False}
        if hostelName:
            filters['hostelName'] = hostelName
        if blockName:
            filters['blockName'] = blockName
        if floorNumber is not None:
            filters['floorNumber'] = floorNumber
        if isAC is not None:
            filters['isAC'] = isAC
        if isDeluxe is not None:
            filters['isDeluxe'] = isDeluxe
        if isApartment is not None:
            filters['isApartment'] = isApartment
            
        all_rooms = room.get_all_rooms(filters)
        
        return {"success": True, "data": all_rooms, "count": len(all_rooms)}
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
        # Map API fields (snake_case) to database fields (camelCase)
        db_data = {
            'userId': pref.user_id,
            'preferenceRank': pref.priority,  # API uses 'priority', DB uses 'preferenceRank'
            'roomId': pref.room_id
        }
        result = preference.create_preference(db_data)
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
        # Get requests where user is the requester
        conn = psycopg2.connect(**room.DB_CONFIG)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
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
        conn = psycopg2.connect(**room.DB_CONFIG)
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

# ==================== DISABLED: Roommate Approval Endpoints ====================
# These endpoints are disabled because RoommateApproval table was removed during denormalization
# TODO: Reimplement if this feature is needed

# @app.post("/api/approvals", tags=["Approval"])
# def send_approval_request_endpoint(approval: ApprovalRequest):
#     """Send a roommate approval request - DISABLED"""
#     raise HTTPException(status_code=501, detail="Roommate approval feature temporarily disabled")

# @app.put("/api/approvals/{approval_id}/approve", tags=["Approval"])
# def approve_request_endpoint(approval_id: int):
#     """Approve a roommate request - DISABLED"""
#     raise HTTPException(status_code=501, detail="Roommate approval feature temporarily disabled")

# @app.put("/api/approvals/{approval_id}/reject", tags=["Approval"])
# def reject_request_endpoint(approval_id: int):
#     """Reject a roommate request - DISABLED"""
#     raise HTTPException(status_code=501, detail="Roommate approval feature temporarily disabled")

# ==================== Room Assignment Endpoints ====================
# NOTE: Room assignments are now handled through the RoomAssignments table

@app.get("/api/assignments/{user_id}", tags=["Assignment"])
def get_user_assignment(user_id: int):
    """Get room assignment for a user"""
    try:
        conn = psycopg2.connect(**room.DB_CONFIG)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        query = """
            SELECT 
                r.id as "roomId",
                r."roomNumber",
                r."floorNumber",
                r."blockName",
                r."hostelName",
                r."capacity",
                r."occupied",
                r."isAC",
                r."isDeluxe",
                r."isApartment",
                ra."assignedAt"
            FROM "RoomAssignments" ra
            JOIN "Rooms" r ON ra."roomId" = r.id
            WHERE ra."userId" = %s
        """
        cursor.execute(query, (user_id,))
        result = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        if not result:
            raise HTTPException(status_code=404, detail="No assignment found for user")
        return {"success": True, "data": dict(result)}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/assignments/room/{room_id}", tags=["Assignment"])
def get_room_assignments(room_id: int):
    """Get all users assigned to a room"""
    try:
        conn = psycopg2.connect(**room.DB_CONFIG)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        query = """
            SELECT 
                r.id as "roomId",
                r."roomNumber",
                r."floorNumber",
                r."blockName",
                r."hostelName",
                r."capacity",
                r."occupied",
                json_agg(json_build_object(
                    'userId', u.id,
                    'name', u.name,
                    'email', u.email,
                    'rank', u.rank,
                    'assignedAt', ra."assignedAt"
                )) as "assignedUsers"
            FROM "Rooms" r
            LEFT JOIN "RoomAssignments" ra ON r.id = ra."roomId"
            LEFT JOIN "User" u ON ra."userId" = u.id
            WHERE r.id = %s
            GROUP BY r.id, r."roomNumber", r."floorNumber", r."blockName", r."hostelName", r."capacity", r."occupied"
        """
        cursor.execute(query, (room_id,))
        result = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        if not result:
            raise HTTPException(status_code=404, detail="Room not found")
        return {"success": True, "data": dict(result)}
    except HTTPException:
        raise
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

# ==================== DEPRECATED ENDPOINTS ====================
# The following endpoints are commented out because RoommateApproval and RoomLock 
# tables have been removed during denormalization. Room locking is now handled
# directly through the Rooms table (isLocked, lockedByUserId, lockExpiresAt fields).

# # RoommateApproval Endpoints (DISABLED - Table removed)
# @app.post("/roommate-approval/")
# def send_roommate_approval(data: dict):
#     # TODO: Reimplement using new schema
#     raise HTTPException(status_code=501, detail="Feature temporarily disabled during migration")

# @app.post("/roommate-approval/{approval_id}/accept")
# def accept_roommate_approval(approval_id: int):
#     raise HTTPException(status_code=501, detail="Feature temporarily disabled during migration")

# @app.post("/roommate-approval/{approval_id}/reject")
# def reject_roommate_approval(approval_id: int):
#     raise HTTPException(status_code=501, detail="Feature temporarily disabled during migration")

# @app.get("/roommate-approval/{user_id}/status")
# def check_roommate_approval_status(user_id: int):
#     raise HTTPException(status_code=501, detail="Feature temporarily disabled during migration")

# @app.get("/roommate-approval/{user_id}/pending")
# def get_pending_roommate_approvals(user_id: int):
#     raise HTTPException(status_code=501, detail="Feature temporarily disabled during migration")

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

# RoomLock Endpoints - Now handled through Rooms table directly
@app.post("/room-lock/")
def lock_room(data: dict):
    """Lock a room for a user"""
    try:
        room_id = data.get("roomId")
        user_id = data.get("userId")
        expires_at = data.get("expiresAt")
        
        if not room_id or not user_id:
            raise HTTPException(status_code=400, detail="roomId and userId are required")
        
        conn = psycopg2.connect(**room.DB_CONFIG)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Check if room is already locked
        check_query = 'SELECT "isLocked", "lockedByUserId" FROM "Rooms" WHERE id = %s'
        cursor.execute(check_query, (room_id,))
        room_data = cursor.fetchone()
        
        if not room_data:
            cursor.close()
            conn.close()
            raise HTTPException(status_code=404, detail="Room not found")
        
        if room_data["isLocked"] and room_data["lockedByUserId"] != user_id:
            cursor.close()
            conn.close()
            raise HTTPException(status_code=409, detail="Room is already locked by another user")
        
        # Lock the room
        update_query = '''
            UPDATE "Rooms" 
            SET "isLocked" = true, 
                "lockedByUserId" = %s, 
                "lockedAt" = CURRENT_TIMESTAMP,
                "lockExpiresAt" = %s
            WHERE id = %s
            RETURNING *
        '''
        cursor.execute(update_query, (user_id, expires_at, room_id))
        result = cursor.fetchone()
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return {"success": True, "message": "Room locked successfully", "data": dict(result)}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/room-lock/{room_id}/unlock")
def unlock_room(room_id: int, user_id: int = Body(..., embed=True)):
    """Unlock a room"""
    try:
        conn = psycopg2.connect(**room.DB_CONFIG)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Check if room is locked by this user
        check_query = 'SELECT "isLocked", "lockedByUserId" FROM "Rooms" WHERE id = %s'
        cursor.execute(check_query, (room_id,))
        room_data = cursor.fetchone()
        
        if not room_data:
            cursor.close()
            conn.close()
            raise HTTPException(status_code=404, detail="Room not found")
        
        if not room_data["isLocked"]:
            cursor.close()
            conn.close()
            raise HTTPException(status_code=400, detail="Room is not locked")
        
        if room_data["lockedByUserId"] != user_id:
            cursor.close()
            conn.close()
            raise HTTPException(status_code=403, detail="You don't have permission to unlock this room")
        
        # Unlock the room
        update_query = '''
            UPDATE "Rooms" 
            SET "isLocked" = false, 
                "lockedByUserId" = NULL, 
                "lockedAt" = NULL,
                "lockExpiresAt" = NULL
            WHERE id = %s
            RETURNING *
        '''
        cursor.execute(update_query, (room_id,))
        result = cursor.fetchone()
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return {"success": True, "message": "Room unlocked successfully", "data": dict(result)}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/room-lock/{room_id}/status")
def check_room_lock_status(room_id: int):
    """Check if a room is locked"""
    try:
        conn = psycopg2.connect(**room.DB_CONFIG)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        query = '''
            SELECT 
                id as "roomId",
                "roomNumber",
                "isLocked",
                "lockedByUserId",
                "lockedAt",
                "lockExpiresAt"
            FROM "Rooms"
            WHERE id = %s
        '''
        cursor.execute(query, (room_id,))
        result = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        if not result:
            raise HTTPException(status_code=404, detail="Room not found")
        
        return {"success": True, "data": dict(result)}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/room-lock/{room_id}")
def remove_room_lock(room_id: int, user_id: int = Body(..., embed=True)):
    """Forcefully remove a room lock (admin only)"""
    # Note: This should ideally check for admin permissions
    try:
        conn = psycopg2.connect(**room.DB_CONFIG)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        update_query = '''
            UPDATE "Rooms" 
            SET "isLocked" = false, 
                "lockedByUserId" = NULL, 
                "lockedAt" = NULL,
                "lockExpiresAt" = NULL
            WHERE id = %s
            RETURNING *
        '''
        cursor.execute(update_query, (room_id,))
        result = cursor.fetchone()
        
        if not result:
            conn.rollback()
            cursor.close()
            conn.close()
            raise HTTPException(status_code=404, detail="Room not found")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return {"success": True, "message": "Room lock removed successfully", "data": dict(result)}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


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

