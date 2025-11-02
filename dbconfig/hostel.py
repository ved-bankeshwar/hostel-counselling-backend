"""CRUD operations for Hostel model."""

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


def create_hostel(data: Dict[str, Any]) -> Dict[str, Any]:
    """Create a new hostel."""
    conn = get_connection()
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(
            'INSERT INTO "Hostel" (name) VALUES (%(name)s) RETURNING *',
            {'name': data['name']}
        )
        hostel = dict(cursor.fetchone())
        conn.commit()
        cursor.close()
        return hostel
    except Exception as e:
        conn.rollback()
        raise Exception(f"Error creating hostel: {str(e)}")
    finally:
        conn.close()


def get_hostel_by_id(hostel_id: int) -> Optional[Dict[str, Any]]:
    """Get hostel by ID."""
    conn = get_connection()
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute('SELECT * FROM "Hostel" WHERE id = %s', (hostel_id,))
        hostel = cursor.fetchone()
        cursor.close()
        return dict(hostel) if hostel else None
    except Exception as e:
        raise Exception(f"Error fetching hostel: {str(e)}")
    finally:
        conn.close()


def get_all_hostels() -> List[Dict[str, Any]]:
    """Get all hostels."""
    conn = get_connection()
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute('SELECT * FROM "Hostel"')
        hostels = [dict(row) for row in cursor.fetchall()]
        cursor.close()
        return hostels
    except Exception as e:
        raise Exception(f"Error fetching hostels: {str(e)}")
    finally:
        conn.close()


def update_hostel(hostel_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
    """Update hostel by ID."""
    conn = get_connection()
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        set_clauses = []
        params = []
        for key, value in data.items():
            set_clauses.append(f'"{key}" = %s')
            params.append(value)
        params.append(hostel_id)
        
        query = f'UPDATE "Hostel" SET {", ".join(set_clauses)} WHERE id = %s RETURNING *'
        cursor.execute(query, params)
        hostel = dict(cursor.fetchone())
        conn.commit()
        cursor.close()
        return hostel
    except Exception as e:
        conn.rollback()
        raise Exception(f"Error updating hostel: {str(e)}")
    finally:
        conn.close()


def delete_hostel(hostel_id: int) -> Dict[str, Any]:
    """Delete hostel by ID."""
    conn = get_connection()
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute('DELETE FROM "Hostel" WHERE id = %s RETURNING *', (hostel_id,))
        hostel = dict(cursor.fetchone())
        conn.commit()
        cursor.close()
        return hostel
    except Exception as e:
        conn.rollback()
        raise Exception(f"Error deleting hostel: {str(e)}")
    finally:
        conn.close()


def get_hostel_by_name(name: str) -> Optional[Dict[str, Any]]:
    """Get hostel by name."""
    conn = get_connection()
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute('SELECT * FROM "Hostel" WHERE name = %s', (name,))
        hostel = cursor.fetchone()
        cursor.close()
        return dict(hostel) if hostel else None
    except Exception as e:
        raise Exception(f"Error fetching hostel by name: {str(e)}")
    finally:
        conn.close()

