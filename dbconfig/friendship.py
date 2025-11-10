"""CRUD operations for Friendship model."""

import psycopg2
from psycopg2.extras import RealDictCursor
from typing import Optional, List, Dict, Any
import sys
import os

# Add parent directory to path to import config
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import DB_CONFIG


def get_connection():
    """Create and return a database connection."""
    return psycopg2.connect(**DB_CONFIG)


def create_friendship(data: Dict[str, Any]) -> Dict[str, Any]:
    """Create a new friendship."""
    conn = get_connection()
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(
            """
            INSERT INTO "Friendship" ("userId", "friendId", status)
            VALUES (%(userId)s, %(friendId)s, %(status)s)
            RETURNING *
            """,
            {
                'userId': data['userId'],
                'friendId': data['friendId'],
                'status': data.get('status', 'pending'),
            }
        )
        friendship = dict(cursor.fetchone())
        conn.commit()
        cursor.close()
        return friendship
    except Exception as e:
        conn.rollback()
        raise Exception(f"Error creating friendship: {str(e)}")
    finally:
        conn.close()


def get_friendship_by_id(friendship_id: int) -> Optional[Dict[str, Any]]:
    """Get friendship by ID."""
    conn = get_connection()
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute('SELECT * FROM "Friendship" WHERE id = %s', (friendship_id,))
        friendship = cursor.fetchone()
        cursor.close()
        return dict(friendship) if friendship else None
    except Exception as e:
        raise Exception(f"Error fetching friendship: {str(e)}")
    finally:
        conn.close()


def get_all_friendships(filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    """Get all friendships with optional filters."""
    conn = get_connection()
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        query = 'SELECT * FROM "Friendship"'
        params = []
        
        if filters:
            conditions = []
            for key, value in filters.items():
                conditions.append(f'"{key}" = %s')
                params.append(value)
            query += ' WHERE ' + ' AND '.join(conditions)
        
        cursor.execute(query, params)
        friendships = [dict(row) for row in cursor.fetchall()]
        cursor.close()
        return friendships
    except Exception as e:
        raise Exception(f"Error fetching friendships: {str(e)}")
    finally:
        conn.close()


def update_friendship(friendship_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
    """Update friendship by ID."""
    conn = get_connection()
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        set_clauses = []
        params = []
        for key, value in data.items():
            set_clauses.append(f'"{key}" = %s')
            params.append(value)
        params.append(friendship_id)
        
        query = f'UPDATE "Friendship" SET {", ".join(set_clauses)} WHERE id = %s RETURNING *'
        cursor.execute(query, params)
        friendship = dict(cursor.fetchone())
        conn.commit()
        cursor.close()
        return friendship
    except Exception as e:
        conn.rollback()
        raise Exception(f"Error updating friendship: {str(e)}")
    finally:
        conn.close()


def delete_friendship(friendship_id: int) -> Dict[str, Any]:
    """Delete friendship by ID."""
    conn = get_connection()
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute('DELETE FROM "Friendship" WHERE id = %s RETURNING *', (friendship_id,))
        friendship = dict(cursor.fetchone())
        conn.commit()
        cursor.close()
        return friendship
    except Exception as e:
        conn.rollback()
        raise Exception(f"Error deleting friendship: {str(e)}")
    finally:
        conn.close()


def get_friendships_by_user_id(user_id: int) -> List[Dict[str, Any]]:
    """Get all friendships for a user (sent and received)."""
    conn = get_connection()
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(
            'SELECT * FROM "Friendship" WHERE "userId" = %s OR "friendId" = %s',
            (user_id, user_id)
        )
        friendships = [dict(row) for row in cursor.fetchall()]
        cursor.close()
        return friendships
    except Exception as e:
        raise Exception(f"Error fetching friendships by user ID: {str(e)}")
    finally:
        conn.close()


def update_friendship_status(user_id: int, friend_id: int, status: str) -> int:
    """Update friendship status between two users."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            'UPDATE "Friendship" SET status = %s WHERE "userId" = %s AND "friendId" = %s',
            (status, user_id, friend_id)
        )
        count = cursor.rowcount
        conn.commit()
        cursor.close()
        return count
    except Exception as e:
        conn.rollback()
        raise Exception(f"Error updating friendship status: {str(e)}")
    finally:
        conn.close()


def get_accepted_friends(user_id: int) -> List[Dict[str, Any]]:
    """Get all accepted friends for a user."""
    conn = get_connection()
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(
            """
            SELECT * FROM "Friendship" 
            WHERE ("userId" = %s OR "friendId" = %s) AND status = 'accepted'
            """,
            (user_id, user_id)
        )
        friendships = [dict(row) for row in cursor.fetchall()]
        cursor.close()
        return friendships
    except Exception as e:
        raise Exception(f"Error fetching accepted friends: {str(e)}")
    finally:
        conn.close()

