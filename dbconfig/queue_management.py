"""CRUD operations for TurnQueue and ProcessingQueue models."""

import psycopg2
from psycopg2.extras import RealDictCursor
from typing import Optional, List, Dict, Any

# Database connection parameters
DB_CONFIG = {
    'host': 'localhost',
    'port': 5433,
    'database': 'room_counselling',
    'user': 'admin',
    'password': 'admin'
}


def get_connection():
    """Create and return a database connection."""
    return psycopg2.connect(**DB_CONFIG)


# ===================== TURN QUEUE OPERATIONS =====================

def initialize_turn_queue() -> int:
    """Initialize turn queue with all users sorted by rank."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO "TurnQueue" ("userId", rank, status)
            SELECT id, rank, 'pending'
            FROM "User"
            WHERE "isActive" = true
            ORDER BY rank
            ON CONFLICT ("userId") DO NOTHING
            """
        )
        count = cursor.rowcount
        conn.commit()
        cursor.close()
        return count
    except Exception as e:
        conn.rollback()
        raise Exception(f"Error initializing turn queue: {str(e)}")
    finally:
        conn.close()


def get_turn_by_rank(rank: int) -> Optional[Dict[str, Any]]:
    """Get turn queue entry by rank."""
    conn = get_connection()
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(
            """
            SELECT tq.*, u.name, u.email, u."registrationNumber"
            FROM "TurnQueue" tq
            JOIN "User" u ON tq."userId" = u.id
            WHERE tq.rank = %s
            """,
            (rank,)
        )
        turn = cursor.fetchone()
        cursor.close()
        return dict(turn) if turn else None
    except Exception as e:
        raise Exception(f"Error fetching turn by rank: {str(e)}")
    finally:
        conn.close()


def get_turn_by_user_id(user_id: int) -> Optional[Dict[str, Any]]:
    """Get turn queue entry by user ID."""
    conn = get_connection()
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(
            'SELECT * FROM "TurnQueue" WHERE "userId" = %s',
            (user_id,)
        )
        turn = cursor.fetchone()
        cursor.close()
        return dict(turn) if turn else None
    except Exception as e:
        raise Exception(f"Error fetching turn by user ID: {str(e)}")
    finally:
        conn.close()


def start_turn(rank: int) -> Dict[str, Any]:
    """Mark a turn as active and set start time."""
    conn = get_connection()
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(
            """
            UPDATE "TurnQueue"
            SET status = 'active',
                "turnStartTime" = CURRENT_TIMESTAMP
            WHERE rank = %s
            RETURNING *
            """,
            (rank,)
        )
        turn = dict(cursor.fetchone())
        conn.commit()
        cursor.close()
        return turn
    except Exception as e:
        conn.rollback()
        raise Exception(f"Error starting turn: {str(e)}")
    finally:
        conn.close()


def lock_turn(user_id: int) -> Dict[str, Any]:
    """Lock a user's turn (they've submitted preferences)."""
    conn = get_connection()
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(
            """
            UPDATE "TurnQueue"
            SET "lockedAt" = CURRENT_TIMESTAMP,
                "turnEndTime" = CURRENT_TIMESTAMP
            WHERE "userId" = %s
            RETURNING *
            """,
            (user_id,)
        )
        turn = dict(cursor.fetchone())
        conn.commit()
        cursor.close()
        return turn
    except Exception as e:
        conn.rollback()
        raise Exception(f"Error locking turn: {str(e)}")
    finally:
        conn.close()


def complete_turn(rank: int) -> Dict[str, Any]:
    """Mark a turn as completed."""
    conn = get_connection()
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(
            """
            UPDATE "TurnQueue"
            SET status = 'completed',
                "turnEndTime" = CURRENT_TIMESTAMP
            WHERE rank = %s
            RETURNING *
            """,
            (rank,)
        )
        turn = dict(cursor.fetchone())
        conn.commit()
        cursor.close()
        return turn
    except Exception as e:
        conn.rollback()
        raise Exception(f"Error completing turn: {str(e)}")
    finally:
        conn.close()


def skip_turn(rank: int) -> Dict[str, Any]:
    """Mark a turn as skipped (timed out without locking)."""
    conn = get_connection()
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(
            """
            UPDATE "TurnQueue"
            SET status = 'skipped',
                "turnEndTime" = CURRENT_TIMESTAMP
            WHERE rank = %s
            RETURNING *
            """,
            (rank,)
        )
        turn = dict(cursor.fetchone())
        conn.commit()
        cursor.close()
        return turn
    except Exception as e:
        conn.rollback()
        raise Exception(f"Error skipping turn: {str(e)}")
    finally:
        conn.close()


def timeout_turn(rank: int) -> Dict[str, Any]:
    """Mark a turn as timed out."""
    conn = get_connection()
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(
            """
            UPDATE "TurnQueue"
            SET status = 'timed_out',
                "turnEndTime" = CURRENT_TIMESTAMP
            WHERE rank = %s
            RETURNING *
            """,
            (rank,)
        )
        turn = dict(cursor.fetchone())
        conn.commit()
        cursor.close()
        return turn
    except Exception as e:
        conn.rollback()
        raise Exception(f"Error timing out turn: {str(e)}")
    finally:
        conn.close()


def get_pending_turns() -> List[Dict[str, Any]]:
    """Get all pending turns."""
    conn = get_connection()
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(
            """
            SELECT tq.*, u.name, u.email
            FROM "TurnQueue" tq
            JOIN "User" u ON tq."userId" = u.id
            WHERE tq.status = 'pending'
            ORDER BY tq.rank
            """
        )
        turns = [dict(row) for row in cursor.fetchall()]
        cursor.close()
        return turns
    except Exception as e:
        raise Exception(f"Error fetching pending turns: {str(e)}")
    finally:
        conn.close()


# ===================== PROCESSING QUEUE OPERATIONS =====================

def add_to_processing_queue(user_id: int, rank: int) -> Dict[str, Any]:
    """Add a user to the processing queue."""
    conn = get_connection()
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Get the next queue position
        cursor.execute('SELECT COALESCE(MAX("queuePosition"), 0) + 1 FROM "ProcessingQueue"')
        next_position = cursor.fetchone()[0]
        
        cursor.execute(
            """
            INSERT INTO "ProcessingQueue" ("userId", rank, "queuePosition", "lockedAt", status)
            VALUES (%s, %s, %s, CURRENT_TIMESTAMP, 'queued')
            RETURNING *
            """,
            (user_id, rank, next_position)
        )
        entry = dict(cursor.fetchone())
        conn.commit()
        cursor.close()
        return entry
    except Exception as e:
        conn.rollback()
        raise Exception(f"Error adding to processing queue: {str(e)}")
    finally:
        conn.close()


def get_next_in_processing_queue() -> Optional[Dict[str, Any]]:
    """Get the next queued item to process."""
    conn = get_connection()
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(
            """
            SELECT pq.*, u.name, u.email, u.rank as "userRank"
            FROM "ProcessingQueue" pq
            JOIN "User" u ON pq."userId" = u.id
            WHERE pq.status = 'queued'
            ORDER BY pq."queuePosition"
            LIMIT 1
            """
        )
        entry = cursor.fetchone()
        cursor.close()
        return dict(entry) if entry else None
    except Exception as e:
        raise Exception(f"Error getting next in processing queue: {str(e)}")
    finally:
        conn.close()


def start_processing(entry_id: int) -> Dict[str, Any]:
    """Mark a processing queue entry as being processed."""
    conn = get_connection()
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(
            """
            UPDATE "ProcessingQueue"
            SET status = 'processing'
            WHERE id = %s
            RETURNING *
            """,
            (entry_id,)
        )
        entry = dict(cursor.fetchone())
        conn.commit()
        cursor.close()
        return entry
    except Exception as e:
        conn.rollback()
        raise Exception(f"Error starting processing: {str(e)}")
    finally:
        conn.close()


def complete_processing(entry_id: int, assigned_room_id: Optional[int] = None) -> Dict[str, Any]:
    """Mark a processing queue entry as completed."""
    conn = get_connection()
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(
            """
            UPDATE "ProcessingQueue"
            SET status = 'completed',
                "processedAt" = CURRENT_TIMESTAMP,
                "assignedRoomId" = %s
            WHERE id = %s
            RETURNING *
            """,
            (assigned_room_id, entry_id)
        )
        entry = dict(cursor.fetchone())
        conn.commit()
        cursor.close()
        return entry
    except Exception as e:
        conn.rollback()
        raise Exception(f"Error completing processing: {str(e)}")
    finally:
        conn.close()


def fail_processing(entry_id: int, failure_reason: str) -> Dict[str, Any]:
    """Mark a processing queue entry as failed."""
    conn = get_connection()
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(
            """
            UPDATE "ProcessingQueue"
            SET status = 'failed',
                "processedAt" = CURRENT_TIMESTAMP,
                "failureReason" = %s
            WHERE id = %s
            RETURNING *
            """,
            (failure_reason, entry_id)
        )
        entry = dict(cursor.fetchone())
        conn.commit()
        cursor.close()
        return entry
    except Exception as e:
        conn.rollback()
        raise Exception(f"Error failing processing: {str(e)}")
    finally:
        conn.close()


def get_processing_queue_status() -> Dict[str, int]:
    """Get counts of processing queue by status."""
    conn = get_connection()
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(
            """
            SELECT 
                status,
                COUNT(*) as count
            FROM "ProcessingQueue"
            GROUP BY status
            """
        )
        results = cursor.fetchall()
        cursor.close()
        return {row['status']: row['count'] for row in results}
    except Exception as e:
        raise Exception(f"Error getting processing queue status: {str(e)}")
    finally:
        conn.close()


def get_user_queue_position(user_id: int) -> Optional[int]:
    """Get user's position in processing queue."""
    conn = get_connection()
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(
            'SELECT "queuePosition" FROM "ProcessingQueue" WHERE "userId" = %s AND status = \'queued\'',
            (user_id,)
        )
        result = cursor.fetchone()
        cursor.close()
        return result['queuePosition'] if result else None
    except Exception as e:
        raise Exception(f"Error getting user queue position: {str(e)}")
    finally:
        conn.close()


def get_all_queued_entries() -> List[Dict[str, Any]]:
    """Get all queued entries in processing queue."""
    conn = get_connection()
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(
            """
            SELECT pq.*, u.name, u.email
            FROM "ProcessingQueue" pq
            JOIN "User" u ON pq."userId" = u.id
            WHERE pq.status = 'queued'
            ORDER BY pq."queuePosition"
            """
        )
        entries = [dict(row) for row in cursor.fetchall()]
        cursor.close()
        return entries
    except Exception as e:
        raise Exception(f"Error fetching queued entries: {str(e)}")
    finally:
        conn.close()

