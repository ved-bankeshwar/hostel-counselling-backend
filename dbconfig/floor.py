"""CRUD operations for Floor model."""

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


def create_floor(data: Dict[str, Any]) -> Dict[str, Any]:
    """Create a new floor."""
    conn = get_connection()
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(
            """
            INSERT INTO "Floor" ("blockId", "floorNumber", "totalRooms")
            VALUES (%(blockId)s, %(floorNumber)s, %(totalRooms)s)
            RETURNING *
            """,
            {
                'blockId': data['blockId'],
                'floorNumber': data['floorNumber'],
                'totalRooms': data.get('totalRooms', 40),
            }
        )
        floor = dict(cursor.fetchone())
        conn.commit()
        cursor.close()
        return floor
    except Exception as e:
        conn.rollback()
        raise Exception(f"Error creating floor: {str(e)}")
    finally:
        conn.close()


def get_floor_by_id(floor_id: int) -> Optional[Dict[str, Any]]:
    """Get floor by ID."""
    conn = get_connection()
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute('SELECT * FROM "Floor" WHERE id = %s', (floor_id,))
        floor = cursor.fetchone()
        cursor.close()
        return dict(floor) if floor else None
    except Exception as e:
        raise Exception(f"Error fetching floor: {str(e)}")
    finally:
        conn.close()


def get_all_floors(filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    """Get all floors with optional filters."""
    conn = get_connection()
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        query = 'SELECT * FROM "Floor"'
        params = []
        
        if filters:
            conditions = []
            for key, value in filters.items():
                conditions.append(f'"{key}" = %s')
                params.append(value)
            query += ' WHERE ' + ' AND '.join(conditions)
        
        cursor.execute(query, params)
        floors = [dict(row) for row in cursor.fetchall()]
        cursor.close()
        return floors
    except Exception as e:
        raise Exception(f"Error fetching floors: {str(e)}")
    finally:
        conn.close()


def update_floor(floor_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
    """Update floor by ID."""
    conn = get_connection()
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        set_clauses = []
        params = []
        for key, value in data.items():
            set_clauses.append(f'"{key}" = %s')
            params.append(value)
        params.append(floor_id)
        
        query = f'UPDATE "Floor" SET {", ".join(set_clauses)} WHERE id = %s RETURNING *'
        cursor.execute(query, params)
        floor = dict(cursor.fetchone())
        conn.commit()
        cursor.close()
        return floor
    except Exception as e:
        conn.rollback()
        raise Exception(f"Error updating floor: {str(e)}")
    finally:
        conn.close()


def delete_floor(floor_id: int) -> Dict[str, Any]:
    """Delete floor by ID."""
    conn = get_connection()
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute('DELETE FROM "Floor" WHERE id = %s RETURNING *', (floor_id,))
        floor = dict(cursor.fetchone())
        conn.commit()
        cursor.close()
        return floor
    except Exception as e:
        conn.rollback()
        raise Exception(f"Error deleting floor: {str(e)}")
    finally:
        conn.close()


def get_floors_by_block_id(block_id: int) -> List[Dict[str, Any]]:
    """Get all floors for a specific block."""
    conn = get_connection()
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(
            'SELECT * FROM "Floor" WHERE "blockId" = %s ORDER BY "floorNumber" ASC',
            (block_id,)
        )
        floors = [dict(row) for row in cursor.fetchall()]
        cursor.close()
        return floors
    except Exception as e:
        raise Exception(f"Error fetching floors by block ID: {str(e)}")
    finally:
        conn.close()

