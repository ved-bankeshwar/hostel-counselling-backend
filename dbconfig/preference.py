"""CRUD operations for Preference model."""

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


def create_preference(data: Dict[str, Any]) -> Dict[str, Any]:
    """Create a new preference."""
    conn = get_connection()
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(
            """
            INSERT INTO "Preference" ("userId", "preferenceRank", "roomId")
            VALUES (%(userId)s, %(preferenceRank)s, %(roomId)s)
            RETURNING *
            """,
            {
                'userId': data['userId'],
                'preferenceRank': data['preferenceRank'],
                'roomId': data['roomId'],
            }
        )
        preference = dict(cursor.fetchone())
        conn.commit()
        cursor.close()
        return preference
    except Exception as e:
        conn.rollback()
        raise Exception(f"Error creating preference: {str(e)}")
    finally:
        conn.close()


def get_preference_by_id(preference_id: int) -> Optional[Dict[str, Any]]:
    """Get preference by ID."""
    conn = get_connection()
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute('SELECT * FROM "Preference" WHERE id = %s', (preference_id,))
        preference = cursor.fetchone()
        cursor.close()
        return dict(preference) if preference else None
    except Exception as e:
        raise Exception(f"Error fetching preference: {str(e)}")
    finally:
        conn.close()


def get_all_preferences(filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    """Get all preferences with optional filters."""
    conn = get_connection()
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        query = 'SELECT * FROM "Preference"'
        params = []
        
        if filters:
            conditions = []
            for key, value in filters.items():
                conditions.append(f'"{key}" = %s')
                params.append(value)
            query += ' WHERE ' + ' AND '.join(conditions)
        
        cursor.execute(query, params)
        preferences = [dict(row) for row in cursor.fetchall()]
        cursor.close()
        return preferences
    except Exception as e:
        raise Exception(f"Error fetching preferences: {str(e)}")
    finally:
        conn.close()


def update_preference(preference_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
    """Update preference by ID."""
    conn = get_connection()
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        set_clauses = []
        params = []
        for key, value in data.items():
            set_clauses.append(f'"{key}" = %s')
            params.append(value)
        params.append(preference_id)
        
        query = f'UPDATE "Preference" SET {", ".join(set_clauses)} WHERE id = %s RETURNING *'
        cursor.execute(query, params)
        preference = dict(cursor.fetchone())
        conn.commit()
        cursor.close()
        return preference
    except Exception as e:
        conn.rollback()
        raise Exception(f"Error updating preference: {str(e)}")
    finally:
        conn.close()


def delete_preference(preference_id: int) -> Dict[str, Any]:
    """Delete preference by ID."""
    conn = get_connection()
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute('DELETE FROM "Preference" WHERE id = %s RETURNING *', (preference_id,))
        preference = dict(cursor.fetchone())
        conn.commit()
        cursor.close()
        return preference
    except Exception as e:
        conn.rollback()
        raise Exception(f"Error deleting preference: {str(e)}")
    finally:
        conn.close()


def get_preferences_by_user_id(user_id: int) -> List[Dict[str, Any]]:
    """Get all preferences for a specific user, ordered by rank."""
    conn = get_connection()
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(
            'SELECT * FROM "Preference" WHERE "userId" = %s ORDER BY "preferenceRank" ASC',
            (user_id,)
        )
        preferences = [dict(row) for row in cursor.fetchall()]
        cursor.close()
        return preferences
    except Exception as e:
        raise Exception(f"Error fetching preferences by user ID: {str(e)}")
    finally:
        conn.close()


def get_preferences_by_room_id(room_id: int) -> List[Dict[str, Any]]:
    """Get all preferences for a specific room."""
    conn = get_connection()
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(
            'SELECT * FROM "Preference" WHERE "roomId" = %s ORDER BY "preferenceRank" ASC',
            (room_id,)
        )
        preferences = [dict(row) for row in cursor.fetchall()]
        cursor.close()
        return preferences
    except Exception as e:
        raise Exception(f"Error fetching preferences by room ID: {str(e)}")
    finally:
        conn.close()


def delete_preferences_by_user_id(user_id: int) -> int:
    """Delete all preferences for a specific user."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM "Preference" WHERE "userId" = %s', (user_id,))
        count = cursor.rowcount
        conn.commit()
        cursor.close()
        return count
    except Exception as e:
        conn.rollback()
        raise Exception(f"Error deleting preferences by user ID: {str(e)}")
    finally:
        conn.close()


def bulk_create_preferences(preferences_data: List[Dict[str, Any]]) -> int:
    """Bulk create multiple preferences for a user."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        count = 0
        for pref_data in preferences_data:
            cursor.execute(
                """
                INSERT INTO "Preference" ("userId", "preferenceRank", "roomId")
                VALUES (%(userId)s, %(preferenceRank)s, %(roomId)s)
                """,
                pref_data
            )
            count += 1
        conn.commit()
        cursor.close()
        return count
    except Exception as e:
        conn.rollback()
        raise Exception(f"Error bulk creating preferences: {str(e)}")
    finally:
        conn.close()

