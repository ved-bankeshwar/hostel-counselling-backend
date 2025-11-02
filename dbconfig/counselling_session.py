"""CRUD operations for TurnQueue and ProcessingQueue models."""

import psycopg2
from psycopg2.extras import RealDictCursor
from typing import Optional, List, Dict, Any

# Database connection parameters
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'room_counselling',
    'user': 'admin',
    'password': 'admin123'
}

def get_connection():
    """Create and return a database connection."""
    return psycopg2.connect(**DB_CONFIG)


def create_session(session_name: str, turn_duration: int = 30) -> Dict[str, Any]:
    """Create a new counselling session."""
    conn = get_connection()
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(
            """
            INSERT INTO "CounsellingSession" ("sessionName", "turnDuration")
            VALUES (%s, %s)
            RETURNING *
            """,
            (session_name, turn_duration)
        )
        session = dict(cursor.fetchone())
        conn.commit()
        cursor.close()
        return session
    except Exception as e:
        conn.rollback()
        raise Exception(f"Error creating session: {str(e)}")
    finally:
        conn.close()


def get_active_session() -> Optional[Dict[str, Any]]:
    """Get the currently active counselling session."""
    conn = get_connection()
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(
            """
            SELECT * FROM "CounsellingSession" 
            WHERE "sessionStatus" = 'active'
            ORDER BY "createdAt" DESC
            LIMIT 1
            """
        )
        session = cursor.fetchone()
        cursor.close()
        return dict(session) if session else None
    except Exception as e:
        raise Exception(f"Error fetching active session: {str(e)}")
    finally:
        conn.close()


def get_session_by_id(session_id: int) -> Optional[Dict[str, Any]]:
    """Get session by ID."""
    conn = get_connection()
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute('SELECT * FROM "CounsellingSession" WHERE id = %s', (session_id,))
        session = cursor.fetchone()
        cursor.close()
        return dict(session) if session else None
    except Exception as e:
        raise Exception(f"Error fetching session: {str(e)}")
    finally:
        conn.close()


def get_session_by_name(session_name: str) -> Optional[Dict[str, Any]]:
    """Get session by name."""
    conn = get_connection()
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute('SELECT * FROM "CounsellingSession" WHERE "sessionName" = %s', (session_name,))
        session = cursor.fetchone()
        cursor.close()
        return dict(session) if session else None
    except Exception as e:
        raise Exception(f"Error fetching session by name: {str(e)}")
    finally:
        conn.close()


def start_session(session_id: int) -> Dict[str, Any]:
    """Start a counselling session and set it to active."""
    conn = get_connection()
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(
            """
            UPDATE "CounsellingSession" 
            SET "sessionStatus" = 'active', 
                "startedAt" = CURRENT_TIMESTAMP,
                "currentRank" = 1
            WHERE id = %s
            RETURNING *
            """,
            (session_id,)
        )
        session = dict(cursor.fetchone())
        conn.commit()
        cursor.close()
        return session
    except Exception as e:
        conn.rollback()
        raise Exception(f"Error starting session: {str(e)}")
    finally:
        conn.close()


def pause_session(session_id: int) -> Dict[str, Any]:
    """Pause an active counselling session."""
    conn = get_connection()
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(
            """
            UPDATE "CounsellingSession" 
            SET "sessionStatus" = 'paused', 
                "pausedAt" = CURRENT_TIMESTAMP
            WHERE id = %s
            RETURNING *
            """,
            (session_id,)
        )
        session = dict(cursor.fetchone())
        conn.commit()
        cursor.close()
        return session
    except Exception as e:
        conn.rollback()
        raise Exception(f"Error pausing session: {str(e)}")
    finally:
        conn.close()


def resume_session(session_id: int) -> Dict[str, Any]:
    """Resume a paused counselling session."""
    conn = get_connection()
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(
            """
            UPDATE "CounsellingSession" 
            SET "sessionStatus" = 'active', 
                "pausedAt" = NULL
            WHERE id = %s
            RETURNING *
            """,
            (session_id,)
        )
        session = dict(cursor.fetchone())
        conn.commit()
        cursor.close()
        return session
    except Exception as e:
        conn.rollback()
        raise Exception(f"Error resuming session: {str(e)}")
    finally:
        conn.close()


def complete_session(session_id: int) -> Dict[str, Any]:
    """Mark a session as completed."""
    conn = get_connection()
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(
            """
            UPDATE "CounsellingSession" 
            SET "sessionStatus" = 'completed', 
                "completedAt" = CURRENT_TIMESTAMP
            WHERE id = %s
            RETURNING *
            """,
            (session_id,)
        )
        session = dict(cursor.fetchone())
        conn.commit()
        cursor.close()
        return session
    except Exception as e:
        conn.rollback()
        raise Exception(f"Error completing session: {str(e)}")
    finally:
        conn.close()


def update_current_rank(session_id: int, new_rank: int, user_id: Optional[int] = None) -> Dict[str, Any]:
    """Update the current rank being processed."""
    conn = get_connection()
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(
            """
            UPDATE "CounsellingSession" 
            SET "currentRank" = %s,
                "currentUserId" = %s,
                "turnStartTime" = CURRENT_TIMESTAMP
            WHERE id = %s
            RETURNING *
            """,
            (new_rank, user_id, session_id)
        )
        session = dict(cursor.fetchone())
        conn.commit()
        cursor.close()
        return session
    except Exception as e:
        conn.rollback()
        raise Exception(f"Error updating current rank: {str(e)}")
    finally:
        conn.close()


def advance_to_next_rank(session_id: int) -> Dict[str, Any]:
    """Move to the next rank in the session."""
    conn = get_connection()
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Get current rank
        cursor.execute('SELECT "currentRank" FROM "CounsellingSession" WHERE id = %s', (session_id,))
        current = cursor.fetchone()
        if not current:
            raise Exception("Session not found")
        
        next_rank = current['currentRank'] + 1
        
        # Get user with next rank
        cursor.execute('SELECT id FROM "User" WHERE rank = %s', (next_rank,))
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
            RETURNING *
            """,
            (next_rank, next_user_id, session_id)
        )
        session = dict(cursor.fetchone())
        conn.commit()
        cursor.close()
        return session
    except Exception as e:
        conn.rollback()
        raise Exception(f"Error advancing to next rank: {str(e)}")
    finally:
        conn.close()


def get_current_turn_info(session_id: int) -> Optional[Dict[str, Any]]:
    """Get information about the current turn including time remaining."""
    conn = get_connection()
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(
            """
            SELECT 
                cs.*,
                u.name as "userName",
                u.email as "userEmail",
                u."registrationNumber",
                EXTRACT(EPOCH FROM (CURRENT_TIMESTAMP - cs."turnStartTime"))::INTEGER as "elapsedSeconds"
            FROM "CounsellingSession" cs
            LEFT JOIN "User" u ON cs."currentUserId" = u.id
            WHERE cs.id = %s
            """,
            (session_id,)
        )
        info = cursor.fetchone()
        cursor.close()
        
        if info:
            result = dict(info)
            if result.get('elapsedSeconds') is not None and result.get('turnDuration'):
                result['remainingSeconds'] = max(0, result['turnDuration'] - result['elapsedSeconds'])
            return result
        return None
    except Exception as e:
        raise Exception(f"Error getting turn info: {str(e)}")
    finally:
        conn.close()


def is_turn_expired(session_id: int) -> bool:
    """Check if the current turn has expired."""
    info = get_current_turn_info(session_id)
    if not info or not info.get('turnStartTime'):
        return False
    return info.get('remainingSeconds', 0) <= 0


def get_all_sessions() -> list:
    """Get all counselling sessions."""
    conn = get_connection()
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute('SELECT * FROM "CounsellingSession" ORDER BY "createdAt" DESC')
        sessions = [dict(row) for row in cursor.fetchall()]
        cursor.close()
        return sessions
    except Exception as e:
        raise Exception(f"Error fetching all sessions: {str(e)}")
    finally:
        conn.close()

