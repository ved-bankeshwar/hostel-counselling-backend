"""Allocation API endpoints - wraps counselling session for frontend compatibility."""

from fastapi import APIRouter, HTTPException, Header, BackgroundTasks
from pydantic import BaseModel
from typing import Optional
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
import asyncio
from firebase_auth import verify_firebase_token
from friend_requests import get_user_by_firebase_uid

# Database connection parameters
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'room_counselling',
    'user': 'admin',
    'password': 'admin123'
}

router = APIRouter(prefix="/api/allocation", tags=["Allocation"])


def get_connection():
    """Create and return a database connection."""
    return psycopg2.connect(**DB_CONFIG)


class StartSessionRequest(BaseModel):
    sessionName: str
    timePerRank: int = 30


class AllocationSessionResponse(BaseModel):
    id: int
    isActive: bool
    currentRank: int
    totalUsers: int
    startedAt: Optional[str]
    currentUserTurnStartedAt: Optional[str]
    sessionName: str
    timePerRank: int


# Auto-advance manager (singleton)
class AllocationAutoAdvance:
    def __init__(self):
        self.running = False
        self.task = None
    
    async def start_auto_advance(self, session_id: int):
        """Background task to auto-advance ranks every timePerRank seconds."""
        self.running = True
        
        while self.running:
            try:
                conn = get_connection()
                cursor = conn.cursor(cursor_factory=RealDictCursor)
                
                # Get current session
                cursor.execute(
                    'SELECT * FROM "CounsellingSession" WHERE id = %s',
                    (session_id,)
                )
                session = cursor.fetchone()
                
                if not session or session['sessionStatus'] != 'active':
                    cursor.close()
                    conn.close()
                    self.running = False
                    break
                
                # Check if turn time has elapsed
                if session['turnStartTime']:
                    elapsed = (datetime.utcnow() - session['turnStartTime']).total_seconds()
                    
                    if elapsed >= session['turnDuration']:
                        # Move to next rank
                        next_rank = session['currentRank'] + 1
                        
                        # Get total users
                        cursor.execute('SELECT COUNT(*) as total FROM "User" WHERE rank > 0')
                        total_users = cursor.fetchone()['total']
                        
                        if next_rank > total_users:
                            # End session
                            cursor.execute(
                                """
                                UPDATE "CounsellingSession"
                                SET "sessionStatus" = 'completed'::"SessionStatus",
                                    "completedAt" = CURRENT_TIMESTAMP
                                WHERE id = %s
                                """,
                                (session_id,)
                            )
                            conn.commit()
                            cursor.close()
                            conn.close()
                            self.running = False
                            break
                        else:
                            # Get user with next rank
                            cursor.execute(
                                'SELECT id FROM "User" WHERE rank = %s',
                                (next_rank,)
                            )
                            next_user = cursor.fetchone()
                            next_user_id = next_user['id'] if next_user else None
                            
                            # Update session
                            cursor.execute(
                                """
                                UPDATE "CounsellingSession"
                                SET "currentRank" = %s,
                                    "currentUserId" = %s,
                                    "turnStartTime" = CURRENT_TIMESTAMP
                                WHERE id = %s
                                """,
                                (next_rank, next_user_id, session_id)
                            )
                            conn.commit()
                
                cursor.close()
                conn.close()
                
            except Exception as e:
                print(f"Error in auto-advance: {e}")
            
            # Check every 2 seconds
            await asyncio.sleep(2)
    
    def stop(self):
        """Stop the auto-advance background task."""
        self.running = False


auto_advance_manager = AllocationAutoAdvance()


@router.get("/session/current")
async def get_current_allocation_session(authorization: str = Header(None)):
    """
    Get current allocation session status.
    
    **Headers:**
    - Authorization: Bearer <firebase_id_token>
    
    **Response:**
    Returns current session with isActive, currentRank, totalUsers, etc.
    """
    # Verify Firebase token
    if authorization:
        await verify_firebase_token(authorization)
    
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        # Get active session
        cursor.execute("""
            SELECT * FROM "CounsellingSession"
            WHERE "sessionStatus" = 'active'
            ORDER BY "createdAt" DESC
            LIMIT 1
        """)
        
        session = cursor.fetchone()
        
        # Get total users
        cursor.execute('SELECT COUNT(*) as total FROM "User" WHERE rank > 0')
        total_users = cursor.fetchone()['total']
        
        if not session:
            cursor.close()
            conn.close()
            return {
                "success": True,
                "data": {
                    "isActive": False,
                    "currentRank": 0,
                    "totalUsers": total_users
                }
            }
        
        cursor.close()
        conn.close()
        
        return {
            "success": True,
            "data": {
                "id": session['id'],
                "isActive": session['sessionStatus'] == 'active',
                "currentRank": session['currentRank'],
                "totalUsers": total_users,
                "startedAt": session['startedAt'].isoformat() if session['startedAt'] else None,
                "currentUserTurnStartedAt": session['turnStartTime'].isoformat() if session['turnStartTime'] else None,
                "sessionName": session['sessionName'],
                "timePerRank": session['turnDuration']
            }
        }
        
    except Exception as e:
        cursor.close()
        conn.close()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.post("/session/start")
async def start_allocation_session(
    request: StartSessionRequest,
    background_tasks: BackgroundTasks,
    authorization: str = Header(None)
):
    """
    Start allocation session (Admin only).
    
    **Headers:**
    - Authorization: Bearer <firebase_id_token>
    
    **Request Body:**
    - sessionName: Name for the session
    - timePerRank: Seconds per rank (default 30)
    
    **Response:**
    Returns the created session.
    """
    # Verify Firebase token and get user
    decoded_token = await verify_firebase_token(authorization)
    current_user = get_user_by_firebase_uid(decoded_token['uid'])
    
    if not current_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if user is admin
    if current_user.get('role') != 'admin':
        raise HTTPException(status_code=403, detail="Admin access required")
    
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        # Check for existing active session
        cursor.execute("""
            SELECT * FROM "CounsellingSession"
            WHERE "sessionStatus" = 'active'
        """)
        
        existing = cursor.fetchone()
        
        if existing:
            raise HTTPException(
                status_code=400,
                detail="An allocation session is already active"
            )
        
        # Count total users
        cursor.execute('SELECT COUNT(*) as total FROM "User" WHERE rank > 0')
        total_users = cursor.fetchone()['total']
        
        # Get user with rank 1
        cursor.execute('SELECT id FROM "User" WHERE rank = 1')
        first_user = cursor.fetchone()
        first_user_id = first_user['id'] if first_user else None
        
        # Create new session
        cursor.execute("""
            INSERT INTO "CounsellingSession" (
                "sessionName",
                "currentRank",
                "currentUserId",
                "turnStartTime",
                "sessionStatus",
                "turnDuration",
                "startedAt"
            )
            VALUES (%s, 1, %s, CURRENT_TIMESTAMP, 'active'::"SessionStatus", %s, CURRENT_TIMESTAMP)
            RETURNING *
        """, (request.sessionName, first_user_id, request.timePerRank))
        
        session = cursor.fetchone()
        conn.commit()
        cursor.close()
        conn.close()
        
        # Start background auto-advance task
        background_tasks.add_task(auto_advance_manager.start_auto_advance, session['id'])
        
        return {
            "success": True,
            "data": {
                "id": session['id'],
                "isActive": True,
                "currentRank": session['currentRank'],
                "totalUsers": total_users,
                "startedAt": session['startedAt'].isoformat(),
                "timePerRank": session['turnDuration'],
                "sessionName": session['sessionName']
            },
            "message": "Allocation session started"
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


@router.post("/session/stop")
async def stop_allocation_session(authorization: str = Header(None)):
    """
    Stop allocation session (Admin only).
    
    **Headers:**
    - Authorization: Bearer <firebase_id_token>
    """
    # Verify Firebase token and get user
    decoded_token = await verify_firebase_token(authorization)
    current_user = get_user_by_firebase_uid(decoded_token['uid'])
    
    if not current_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if user is admin
    if current_user.get('role') != 'admin':
        raise HTTPException(status_code=403, detail="Admin access required")
    
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        cursor.execute("""
            UPDATE "CounsellingSession"
            SET "sessionStatus" = 'completed'::"SessionStatus",
                "completedAt" = CURRENT_TIMESTAMP
            WHERE "sessionStatus" = 'active'
            RETURNING *
        """)
        
        session = cursor.fetchone()
        
        if not session:
            raise HTTPException(status_code=404, detail="No active session found")
        
        # Clear all room assignments from RoomAssignments table
        cursor.execute('DELETE FROM "RoomAssignments"')
        
        # Clear all preferences when session ends
        cursor.execute('DELETE FROM "Preference"')
        
        # Reset all rooms (clear deprecated fields and reset occupied count)
        cursor.execute("""
            UPDATE "Rooms"
            SET "assignedUserId" = NULL,
                "assignedAt" = NULL,
                occupied = 0,
                "isLocked" = false,
                "lockedByUserId" = NULL,
                "lockedAt" = NULL,
                "lockExpiresAt" = NULL
        """)
        
        conn.commit()
        cursor.close()
        conn.close()
        
        # Stop auto-advance
        auto_advance_manager.stop()
        
        return {
            "success": True,
            "message": "Allocation session stopped. All preferences and room assignments cleared."
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


@router.post("/clear-all-allocations")
async def clear_all_allocations(authorization: str = Header(None)):
    """
    Clear all room allocations and preferences (Admin only).
    This does NOT stop the session, just clears all assignments.
    
    **Headers:**
    - Authorization: Bearer <firebase_id_token>
    
    **Response:**
    Returns success message with count of cleared items.
    """
    # Verify Firebase token and get user
    decoded_token = await verify_firebase_token(authorization)
    current_user = get_user_by_firebase_uid(decoded_token['uid'])
    
    if not current_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if user is admin
    if current_user.get('role') != 'admin':
        raise HTTPException(status_code=403, detail="Admin access required")
    
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        # Count current assignments before clearing
        cursor.execute('SELECT COUNT(*) as count FROM "RoomAssignments"')
        assignments_count = cursor.fetchone()['count']
        
        cursor.execute('SELECT COUNT(*) as count FROM "Preference"')
        preferences_count = cursor.fetchone()['count']
        
        # Clear all room assignments from RoomAssignments table
        cursor.execute('DELETE FROM "RoomAssignments"')
        
        # Clear all preferences
        cursor.execute('DELETE FROM "Preference"')
        
        # Reset room occupied counts and clear deprecated fields
        cursor.execute("""
            UPDATE "Rooms"
            SET occupied = 0,
                "assignedUserId" = NULL,
                "assignedAt" = NULL
        """)
        
        # Unlock all rooms
        cursor.execute("""
            UPDATE "Rooms"
            SET "isLocked" = false,
                "lockedByUserId" = NULL,
                "lockedAt" = NULL,
                "lockExpiresAt" = NULL
        """)
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return {
            "success": True,
            "message": "All allocations and preferences cleared successfully",
            "data": {
                "assignmentsCleared": assignments_count,
                "preferencesCleared": preferences_count,
                "roomsReset": True
            }
        }
        
    except Exception as e:
        conn.rollback()
        cursor.close()
        conn.close()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.post("/session/pause")
async def pause_allocation_session(authorization: str = Header(None)):
    """Pause allocation session (Admin only)."""
    decoded_token = await verify_firebase_token(authorization)
    current_user = get_user_by_firebase_uid(decoded_token['uid'])
    
    if not current_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if user is admin
    if current_user.get('role') != 'admin':
        raise HTTPException(status_code=403, detail="Admin access required")
    
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        cursor.execute("""
            UPDATE "CounsellingSession"
            SET "sessionStatus" = 'paused'::"SessionStatus",
                "pausedAt" = CURRENT_TIMESTAMP
            WHERE "sessionStatus" = 'active'
            RETURNING *
        """)
        
        session = cursor.fetchone()
        
        if not session:
            raise HTTPException(status_code=404, detail="No active session found")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        # Stop auto-advance
        auto_advance_manager.stop()
        
        return {"success": True, "message": "Allocation session paused"}
        
    except HTTPException:
        cursor.close()
        conn.close()
        raise
    except Exception as e:
        conn.rollback()
        cursor.close()
        conn.close()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.post("/session/resume")
async def resume_allocation_session(
    background_tasks: BackgroundTasks,
    authorization: str = Header(None)
):
    """Resume paused allocation session (Admin only)."""
    decoded_token = await verify_firebase_token(authorization)
    current_user = get_user_by_firebase_uid(decoded_token['uid'])
    
    if not current_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if user is admin
    if current_user.get('role') != 'admin':
        raise HTTPException(status_code=403, detail="Admin access required")
    
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        cursor.execute("""
            UPDATE "CounsellingSession"
            SET "sessionStatus" = 'active'::"SessionStatus",
                "pausedAt" = NULL,
                "turnStartTime" = CURRENT_TIMESTAMP
            WHERE "sessionStatus" = 'paused'
            RETURNING *
        """)
        
        session = cursor.fetchone()
        
        if not session:
            raise HTTPException(status_code=404, detail="No paused session found")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        # Restart auto-advance
        background_tasks.add_task(auto_advance_manager.start_auto_advance, session['id'])
        
        return {"success": True, "message": "Allocation session resumed"}
        
    except HTTPException:
        cursor.close()
        conn.close()
        raise
    except Exception as e:
        conn.rollback()
        cursor.close()
        conn.close()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.post("/session/next-rank")
async def force_next_rank(authorization: str = Header(None)):
    """Manually move to next rank (Admin only)."""
    decoded_token = await verify_firebase_token(authorization)
    current_user = get_user_by_firebase_uid(decoded_token['uid'])
    
    if not current_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if user is admin
    if current_user.get('role') != 'admin':
        raise HTTPException(status_code=403, detail="Admin access required")
    
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        cursor.execute("""
            SELECT * FROM "CounsellingSession"
            WHERE "sessionStatus" = 'active'
        """)
        
        session = cursor.fetchone()
        
        if not session:
            raise HTTPException(status_code=404, detail="No active session found")
        
        next_rank = session['currentRank'] + 1
        
        # Get total users
        cursor.execute('SELECT COUNT(*) as total FROM "User" WHERE rank > 0')
        total_users = cursor.fetchone()['total']
        
        if next_rank > total_users:
            # End session
            cursor.execute("""
                UPDATE "CounsellingSession"
                SET "sessionStatus" = 'completed'::"SessionStatus",
                    "completedAt" = CURRENT_TIMESTAMP
                WHERE id = %s
                RETURNING *
            """, (session['id'],))
        else:
            # Get user with next rank
            cursor.execute('SELECT id FROM "User" WHERE rank = %s', (next_rank,))
            next_user = cursor.fetchone()
            next_user_id = next_user['id'] if next_user else None
            
            # Update session
            cursor.execute("""
                UPDATE "CounsellingSession"
                SET "currentRank" = %s,
                    "currentUserId" = %s,
                    "turnStartTime" = CURRENT_TIMESTAMP
                WHERE id = %s
                RETURNING *
            """, (next_rank, next_user_id, session['id']))
        
        updated_session = cursor.fetchone()
        conn.commit()
        cursor.close()
        conn.close()
        
        return {
            "success": True,
            "data": {
                "id": updated_session['id'],
                "currentRank": updated_session['currentRank'],
                "isActive": updated_session['sessionStatus'] == 'active'
            },
            "message": "Moved to next rank"
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


class SelectRoomRequest(BaseModel):
    roomId: int


@router.post("/select-room")
async def select_room_during_turn(
    request: SelectRoomRequest,
    authorization: str = Header(None)
):
    """
    User selects a room during their turn - immediately advances to next rank.
    
    **Headers:**
    - Authorization: Bearer <firebase_id_token>
    
    **Request Body:**
    ```json
    {
        "roomId": 42
    }
    ```
    
    **Response (Success - 200):**
    ```json
    {
        "success": true,
        "data": {
            "assignment": {...},
            "room": {...},
            "nextRank": 3,
            "sessionEnded": false
        },
        "message": "Room allocated successfully! Moved to next rank."
    }
    ```
    
    **Error Responses:**
    - 401: Not authenticated
    - 403: Not your turn
    - 404: No active session or room not found
    - 400: Room is full
    """
    # Verify Firebase token and get user
    decoded_token = await verify_firebase_token(authorization)
    current_user = get_user_by_firebase_uid(decoded_token['uid'])
    
    if not current_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        # Get active session
        cursor.execute("""
            SELECT * FROM "CounsellingSession"
            WHERE "sessionStatus" = 'active'
        """)
        
        session = cursor.fetchone()
        
        if not session:
            raise HTTPException(status_code=404, detail="No active allocation session")
        
        # VERIFY IT'S USER'S TURN
        if session['currentRank'] != current_user['rank']:
            raise HTTPException(
                status_code=403,
                detail=f"Not your turn. Current rank: {session['currentRank']}, Your rank: {current_user['rank']}"
            )
        
        # CHECK ROOM EXISTS AND IS AVAILABLE (using new denormalized Rooms table)
        cursor.execute("""
            SELECT * FROM "Rooms"
            WHERE id = %s AND "isLocked" = false
        """, (request.roomId,))
        
        room = cursor.fetchone()
        
        if not room:
            raise HTTPException(status_code=404, detail="Room not found or is locked")
        
        # Check if room has available capacity
        if room['occupied'] >= room['capacity']:
            raise HTTPException(status_code=400, detail="Room is full")
        
        # CHECK IF USER ALREADY HAS AN ASSIGNMENT
        cursor.execute("""
            SELECT * FROM "RoomAssignments" WHERE "userId" = %s
        """, (current_user['id'],))
        
        existing_assignment = cursor.fetchone()
        
        if existing_assignment:
            raise HTTPException(
                status_code=400, 
                detail=f"You have already been assigned to a room (Room ID: {existing_assignment['roomId']})"
            )
        
        # SAVE USER PREFERENCE (track what they selected) - use ON CONFLICT to handle duplicates
        cursor.execute("""
            INSERT INTO "Preference" ("userId", "preferenceRank", "roomId", "createdAt")
            VALUES (%s, 1, %s, CURRENT_TIMESTAMP)
            ON CONFLICT ("userId", "preferenceRank") 
            DO UPDATE SET "roomId" = EXCLUDED."roomId", "createdAt" = CURRENT_TIMESTAMP
            RETURNING *
        """, (current_user['id'], request.roomId))
        
        preference = cursor.fetchone()
        
        # INSERT INTO RoomAssignments table (supports multiple users per room)
        cursor.execute("""
            INSERT INTO "RoomAssignments" ("roomId", "userId", "assignedAt")
            VALUES (%s, %s, CURRENT_TIMESTAMP)
        """, (request.roomId, current_user['id']))
        
        # UPDATE ROOM occupied count
        cursor.execute("""
            UPDATE "Rooms"
            SET occupied = occupied + 1
            WHERE id = %s
        """, (request.roomId,))
        
        # Fetch the updated room info to return
        cursor.execute('SELECT * FROM "Rooms" WHERE id = %s', (request.roomId,))
        updated_room = cursor.fetchone()
        
        # IMMEDIATELY MOVE TO NEXT RANK
        next_rank = session['currentRank'] + 1
        
        # Get total users
        cursor.execute('SELECT COUNT(*) as total FROM "User" WHERE rank > 0')
        total_users = cursor.fetchone()['total']
        
        if next_rank > total_users:
            # End session - all users processed
            cursor.execute("""
                UPDATE "CounsellingSession"
                SET "sessionStatus" = 'completed'::"SessionStatus",
                    "completedAt" = CURRENT_TIMESTAMP
                WHERE id = %s
            """, (session['id'],))
            
            conn.commit()
            
            # Stop auto-advance
            auto_advance_manager.stop()
            
            cursor.close()
            conn.close()
            
            return {
                "success": True,
                "data": {
                    "room": dict(updated_room),
                    "preference": dict(preference),
                    "sessionEnded": True
                },
                "message": "Room allocated successfully! Session completed."
            }
        else:
            # Get user with next rank
            cursor.execute('SELECT id FROM "User" WHERE rank = %s', (next_rank,))
            next_user = cursor.fetchone()
            next_user_id = next_user['id'] if next_user else None
            
            # Update session to next rank
            cursor.execute("""
                UPDATE "CounsellingSession"
                SET "currentRank" = %s,
                    "currentUserId" = %s,
                    "turnStartTime" = CURRENT_TIMESTAMP
                WHERE id = %s
            """, (next_rank, next_user_id, session['id']))
            
            conn.commit()
            cursor.close()
            conn.close()
            
            return {
                "success": True,
                "data": {
                    "room": dict(updated_room),
                    "preference": dict(preference),
                    "nextRank": next_rank,
                    "sessionEnded": False
                },
                "message": "Room allocated successfully! Moved to next rank."
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


# ==================== TEST ENDPOINTS (REMOVE IN PRODUCTION) ====================
# These endpoints bypass Firebase authentication for development testing only
# ⚠️ REMOVE THESE BEFORE DEPLOYING TO PRODUCTION!

@router.post("/session/start-test", deprecated=True)
async def start_allocation_session_test(request: StartSessionRequest, background_tasks: BackgroundTasks):
    """
    TEST ONLY - Start allocation session without Firebase authentication.
    
    ⚠️ REMOVE THIS BEFORE DEPLOYING TO PRODUCTION!
    
    **Request Body:**
    - sessionName: Name for the session
    - timePerRank: Seconds per rank (default 30)
    """
    # Use test user (admin) - bypass Firebase auth
    from dbconfig.user import get_connection as get_user_conn
    
    conn = get_user_conn()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    # Get the admin user
    cursor.execute('SELECT * FROM "User" WHERE role = %s LIMIT 1', ('admin',))
    admin_user = cursor.fetchone()
    cursor.close()
    conn.close()
    
    if not admin_user:
        raise HTTPException(status_code=403, detail="No admin user found in database")
    
    # Now start the session
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        # Check for existing active session
        cursor.execute("""
            SELECT * FROM "CounsellingSession"
            WHERE "sessionStatus" = 'active'
        """)
        
        existing = cursor.fetchone()
        
        if existing:
            cursor.close()
            conn.close()
            raise HTTPException(
                status_code=400,
                detail=f"Active session already exists (ID: {existing['id']}). Stop it first."
            )
        
        # Get first user (lowest rank)
        cursor.execute('SELECT id, rank FROM "User" ORDER BY rank ASC LIMIT 1')
        first_user = cursor.fetchone()
        
        if not first_user:
            cursor.close()
            conn.close()
            raise HTTPException(status_code=400, detail="No users in system")
        
        # Create new session
        cursor.execute(
            """
            INSERT INTO "CounsellingSession" 
            ("sessionStatus", "currentRank", "currentUserId", "startedAt", "turnStartTime", "sessionName", "turnDuration")
            VALUES ('active', %s, %s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, %s, %s)
            RETURNING *
            """,
            (first_user['rank'], first_user['id'], request.sessionName, request.timePerRank)
        )
        
        session = dict(cursor.fetchone())
        
        # Get total users count
        cursor.execute('SELECT COUNT(DISTINCT rank) as count FROM "User"')
        total_users = cursor.fetchone()['count']
        
        conn.commit()
        cursor.close()
        conn.close()
        
        # Start auto-advance in background
        background_tasks.add_task(auto_advance_manager.start_auto_advance, session['id'])
        
        return {
            "success": True,
            "data": {
                "id": session['id'],
                "isActive": True,
                "currentRank": session['currentRank'],
                "totalUsers": total_users,
                "startedAt": str(session['startedAt']),
                "currentUserTurnStartedAt": str(session['turnStartTime']),
                "sessionName": session['sessionName'],
                "timePerRank": session['turnDuration']
            },
            "message": "⚠️ TEST SESSION STARTED - No authentication required",
            "warning": "This endpoint should be removed in production"
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


@router.post("/session/stop-test", deprecated=True)
async def stop_allocation_session_test():
    """
    TEST ONLY - Stop allocation session without Firebase authentication.
    
    ⚠️ REMOVE THIS BEFORE DEPLOYING TO PRODUCTION!
    """
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        cursor.execute("""
            SELECT * FROM "CounsellingSession"
            WHERE "sessionStatus" = 'active'
        """)
        
        session = cursor.fetchone()
        
        if not session:
            cursor.close()
            conn.close()
            raise HTTPException(status_code=404, detail="No active session found")
        
        # Stop the session
        cursor.execute(
            """
            UPDATE "CounsellingSession"
            SET "sessionStatus" = 'completed',
                "completedAt" = CURRENT_TIMESTAMP
            WHERE id = %s
            RETURNING *
            """,
            (session['id'],)
        )
        
        updated = dict(cursor.fetchone())
        
        # Clear all preferences when session ends
        cursor.execute('DELETE FROM "Preference"')
        
        # Reset all room assignments (clear assignedUserId and reset occupied count)
        cursor.execute("""
            UPDATE "Rooms"
            SET "assignedUserId" = NULL,
                "assignedAt" = NULL,
                occupied = 0
        """)
        
        conn.commit()
        
        # Stop auto-advance
        auto_advance_manager.stop()
        
        cursor.close()
        conn.close()
        
        return {
            "success": True,
            "data": updated,
            "message": "⚠️ TEST SESSION STOPPED - No authentication required. All preferences and room assignments cleared.",
            "warning": "This endpoint should be removed in production"
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


@router.get("/session/current-test", deprecated=True)
async def get_current_allocation_session_test():
    """
    TEST ONLY - Get current allocation session without Firebase authentication.
    
    ⚠️ REMOVE THIS BEFORE DEPLOYING TO PRODUCTION!
    """
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        cursor.execute("""
            SELECT * FROM "CounsellingSession"
            WHERE "sessionStatus" = 'active'
            ORDER BY "startedAt" DESC
            LIMIT 1
        """)
        
        session = cursor.fetchone()
        
        if not session:
            cursor.close()
            conn.close()
            return {
                "success": True,
                "data": None,
                "message": "No active session"
            }
        
        # Get total users
        cursor.execute('SELECT COUNT(DISTINCT rank) as count FROM "User"')
        total_users = cursor.fetchone()['count']
        
        cursor.close()
        conn.close()
        
        return {
            "success": True,
            "data": {
                "id": session['id'],
                "isActive": True,
                "currentRank": session['currentRank'],
                "totalUsers": total_users,
                "startedAt": str(session['startedAt']) if session['startedAt'] else None,
                "currentUserTurnStartedAt": str(session['turnStartTime']) if session['turnStartTime'] else None,
                "sessionName": session.get('sessionName', ''),
                "timePerRank": session.get('turnDuration', 30)
            },
            "message": "⚠️ TEST ENDPOINT - No authentication required",
            "warning": "This endpoint should be removed in production"
        }
        
    except Exception as e:
        cursor.close()
        conn.close()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
