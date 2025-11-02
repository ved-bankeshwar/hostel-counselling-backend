"""CRUD operations for RoomLock model."""

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


def create_room_lock(room_id: int, locked_by_user_id: int, lock_duration_seconds: int = 30) -> Dict[str, Any]:
    """Create a temporary lock on a room."""
    conn = get_connection()
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(
            """
            INSERT INTO "RoomLock" ("roomId", "lockedByUserId", "lockDuration")
            VALUES (%s, %s, %s)
            RETURNING *
            """,
            (room_id, locked_by_user_id, lock_duration_seconds)
        )
        lock = dict(cursor.fetchone())
        conn.commit()
        cursor.close()
        return lock
    except Exception as e:
        conn.rollback()
        raise Exception(f"Error creating room lock: {str(e)}")
    finally:
        conn.close()


def get_room_lock(room_id: int) -> Optional[Dict[str, Any]]:
    """Get active lock on a room."""
    conn = get_connection()
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(
            """
            SELECT rl.*,
                   u.name as "lockedByUserName",
                   u."registrationNumber" as "lockedByUserRegNo",
                   EXTRACT(EPOCH FROM (rl."lockedAt" + (rl."lockDuration" || ' seconds')::INTERVAL - CURRENT_TIMESTAMP))::INTEGER as "remainingSeconds"
            FROM "RoomLock" rl
            JOIN "User" u ON rl."lockedByUserId" = u.id
            WHERE rl."roomId" = %s
                AND rl."releasedAt" IS NULL
                AND rl."lockedAt" + (rl."lockDuration" || ' seconds')::INTERVAL > CURRENT_TIMESTAMP
            ORDER BY rl."lockedAt" DESC
            LIMIT 1
            """,
            (room_id,)
        )
        lock = cursor.fetchone()
        cursor.close()
        return dict(lock) if lock else None
    except Exception as e:
        raise Exception(f"Error fetching room lock: {str(e)}")
    finally:
        conn.close()


def is_room_locked(room_id: int) -> bool:
    """Check if a room is currently locked."""
    lock = get_room_lock(room_id)
    return lock is not None


def get_locks_by_user(user_id: int) -> List[Dict[str, Any]]:
    """Get all locks (active and expired) created by a user."""
    conn = get_connection()
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(
            """
            SELECT rl.*,
                   r."roomNumber", r.floor, r."blockId",
                   CASE
                       WHEN rl."releasedAt" IS NOT NULL THEN 'released'
                       WHEN rl."lockedAt" + (rl."lockDuration" || ' seconds')::INTERVAL <= CURRENT_TIMESTAMP THEN 'expired'
                       ELSE 'active'
                   END as "lockStatus"
            FROM "RoomLock" rl
            JOIN "Room" r ON rl."roomId" = r.id
            WHERE rl."lockedByUserId" = %s
            ORDER BY rl."lockedAt" DESC
            """,
            (user_id,)
        )
        locks = [dict(row) for row in cursor.fetchall()]
        cursor.close()
        return locks
    except Exception as e:
        raise Exception(f"Error fetching locks by user: {str(e)}")
    finally:
        conn.close()


def release_lock(lock_id: int) -> Dict[str, Any]:
    """Release a room lock manually."""
    conn = get_connection()
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(
            """
            UPDATE "RoomLock"
            SET "releasedAt" = CURRENT_TIMESTAMP
            WHERE id = %s AND "releasedAt" IS NULL
            RETURNING *
            """,
            (lock_id,)
        )
        lock = cursor.fetchone()
        if not lock:
            raise Exception("Lock not found or already released")
        lock = dict(lock)
        conn.commit()
        cursor.close()
        return lock
    except Exception as e:
        conn.rollback()
        raise Exception(f"Error releasing lock: {str(e)}")
    finally:
        conn.close()


def release_room_lock(room_id: int) -> int:
    """Release all active locks on a specific room."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE "RoomLock"
            SET "releasedAt" = CURRENT_TIMESTAMP
            WHERE "roomId" = %s AND "releasedAt" IS NULL
            """,
            (room_id,)
        )
        count = cursor.rowcount
        conn.commit()
        cursor.close()
        return count
    except Exception as e:
        conn.rollback()
        raise Exception(f"Error releasing room locks: {str(e)}")
    finally:
        conn.close()


def release_user_locks(user_id: int) -> int:
    """Release all active locks created by a user."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE "RoomLock"
            SET "releasedAt" = CURRENT_TIMESTAMP
            WHERE "lockedByUserId" = %s AND "releasedAt" IS NULL
            """,
            (user_id,)
        )
        count = cursor.rowcount
        conn.commit()
        cursor.close()
        return count
    except Exception as e:
        conn.rollback()
        raise Exception(f"Error releasing user locks: {str(e)}")
    finally:
        conn.close()


def clean_expired_locks() -> int:
    """Clean up expired locks (optional, for database maintenance)."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE "RoomLock"
            SET "releasedAt" = "lockedAt" + ("lockDuration" || ' seconds')::INTERVAL
            WHERE "releasedAt" IS NULL
                AND "lockedAt" + ("lockDuration" || ' seconds')::INTERVAL <= CURRENT_TIMESTAMP
            """,
        )
        count = cursor.rowcount
        conn.commit()
        cursor.close()
        return count
    except Exception as e:
        conn.rollback()
        raise Exception(f"Error cleaning expired locks: {str(e)}")
    finally:
        conn.close()


def get_all_active_locks() -> List[Dict[str, Any]]:
    """Get all currently active room locks."""
    conn = get_connection()
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(
            """
            SELECT rl.*,
                   r."roomNumber", r.floor, r."blockId",
                   u.name as "lockedByUserName",
                   u."registrationNumber" as "lockedByUserRegNo",
                   EXTRACT(EPOCH FROM (rl."lockedAt" + (rl."lockDuration" || ' seconds')::INTERVAL - CURRENT_TIMESTAMP))::INTEGER as "remainingSeconds"
            FROM "RoomLock" rl
            JOIN "Room" r ON rl."roomId" = r.id
            JOIN "User" u ON rl."lockedByUserId" = u.id
            WHERE rl."releasedAt" IS NULL
                AND rl."lockedAt" + (rl."lockDuration" || ' seconds')::INTERVAL > CURRENT_TIMESTAMP
            ORDER BY rl."lockedAt" DESC
            """
        )
        locks = [dict(row) for row in cursor.fetchall()]
        cursor.close()
        return locks
    except Exception as e:
        raise Exception(f"Error fetching all active locks: {str(e)}")
    finally:
        conn.close()


def extend_lock(lock_id: int, additional_seconds: int) -> Dict[str, Any]:
    """Extend an existing lock duration."""
    conn = get_connection()
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(
            """
            UPDATE "RoomLock"
            SET "lockDuration" = "lockDuration" + %s
            WHERE id = %s AND "releasedAt" IS NULL
            RETURNING *
            """,
            (additional_seconds, lock_id)
        )
        lock = cursor.fetchone()
        if not lock:
            raise Exception("Lock not found or already released")
        lock = dict(lock)
        conn.commit()
        cursor.close()
        return lock
    except Exception as e:
        conn.rollback()
        raise Exception(f"Error extending lock: {str(e)}")
    finally:
        conn.close()


def get_lock_history_for_room(room_id: int) -> List[Dict[str, Any]]:
    """Get full lock history for a room."""
    conn = get_connection()
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(
            """
            SELECT rl.*,
                   u.name as "lockedByUserName",
                   u."registrationNumber" as "lockedByUserRegNo",
                   CASE
                       WHEN rl."releasedAt" IS NOT NULL THEN 'released'
                       WHEN rl."lockedAt" + (rl."lockDuration" || ' seconds')::INTERVAL <= CURRENT_TIMESTAMP THEN 'expired'
                       ELSE 'active'
                   END as "lockStatus"
            FROM "RoomLock" rl
            JOIN "User" u ON rl."lockedByUserId" = u.id
            WHERE rl."roomId" = %s
            ORDER BY rl."lockedAt" DESC
            """,
            (room_id,)
        )
        locks = [dict(row) for row in cursor.fetchall()]
        cursor.close()
        return locks
    except Exception as e:
        raise Exception(f"Error fetching lock history: {str(e)}")
    finally:
        conn.close()

