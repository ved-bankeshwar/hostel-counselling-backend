"""CRUD operations for Room model."""

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


def create_room(data: Dict[str, Any]) -> Dict[str, Any]:
    """Create a new room."""
    conn = get_connection()
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(
            """
            INSERT INTO "Room" ("floorId", "roomNumber", capacity, occupied)
            VALUES (%(floorId)s, %(roomNumber)s, %(capacity)s, %(occupied)s)
            RETURNING *
            """,
            {
                'floorId': data['floorId'],
                'roomNumber': data['roomNumber'],
                'capacity': data['capacity'],
                'occupied': data.get('occupied', 0),
            }
        )
        room = dict(cursor.fetchone())
        conn.commit()
        cursor.close()
        return room
    except Exception as e:
        conn.rollback()
        raise Exception(f"Error creating room: {str(e)}")
    finally:
        conn.close()


def get_room_by_id(room_id: int) -> Optional[Dict[str, Any]]:
    """Get room by ID."""
    conn = get_connection()
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute('SELECT * FROM "Room" WHERE id = %s', (room_id,))
        room = cursor.fetchone()
        cursor.close()
        return dict(room) if room else None
    except Exception as e:
        raise Exception(f"Error fetching room: {str(e)}")
    finally:
        conn.close()


def get_all_rooms(filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    """Get all rooms with optional filters."""
    conn = get_connection()
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        query = 'SELECT * FROM "Room"'
        params = []
        
        if filters:
            conditions = []
            for key, value in filters.items():
                conditions.append(f'"{key}" = %s')
                params.append(value)
            query += ' WHERE ' + ' AND '.join(conditions)
        
        cursor.execute(query, params)
        rooms = [dict(row) for row in cursor.fetchall()]
        cursor.close()
        return rooms
    except Exception as e:
        raise Exception(f"Error fetching rooms: {str(e)}")
    finally:
        conn.close()


def update_room(room_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
    """Update room by ID."""
    conn = get_connection()
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        set_clauses = []
        params = []
        for key, value in data.items():
            set_clauses.append(f'"{key}" = %s')
            params.append(value)
        params.append(room_id)
        
        query = f'UPDATE "Room" SET {", ".join(set_clauses)} WHERE id = %s RETURNING *'
        cursor.execute(query, params)
        room = dict(cursor.fetchone())
        conn.commit()
        cursor.close()
        return room
    except Exception as e:
        conn.rollback()
        raise Exception(f"Error updating room: {str(e)}")
    finally:
        conn.close()


def delete_room(room_id: int) -> Dict[str, Any]:
    """Delete room by ID."""
    conn = get_connection()
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute('DELETE FROM "Room" WHERE id = %s RETURNING *', (room_id,))
        room = dict(cursor.fetchone())
        conn.commit()
        cursor.close()
        return room
    except Exception as e:
        conn.rollback()
        raise Exception(f"Error deleting room: {str(e)}")
    finally:
        conn.close()


def get_rooms_by_floor_id(floor_id: int) -> List[Dict[str, Any]]:
    """Get all rooms for a specific floor."""
    conn = get_connection()
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute('SELECT * FROM "Room" WHERE "floorId" = %s', (floor_id,))
        rooms = [dict(row) for row in cursor.fetchall()]
        cursor.close()
        return rooms
    except Exception as e:
        raise Exception(f"Error fetching rooms by floor ID: {str(e)}")
    finally:
        conn.close()


def get_available_rooms() -> List[Dict[str, Any]]:
    """Get all rooms that are not fully occupied."""
    conn = get_connection()
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute('SELECT * FROM "Room" WHERE occupied < capacity')
        rooms = [dict(row) for row in cursor.fetchall()]
        cursor.close()
        return rooms
    except Exception as e:
        raise Exception(f"Error fetching available rooms: {str(e)}")
    finally:
        conn.close()


def increment_room_occupancy(room_id: int) -> Dict[str, Any]:
    """Increment room occupancy by 1."""
    conn = get_connection()
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(
            'UPDATE "Room" SET occupied = occupied + 1 WHERE id = %s RETURNING *',
            (room_id,)
        )
        room = dict(cursor.fetchone())
        conn.commit()
        cursor.close()
        return room
    except Exception as e:
        conn.rollback()
        raise Exception(f"Error incrementing room occupancy: {str(e)}")
    finally:
        conn.close()


def decrement_room_occupancy(room_id: int) -> Dict[str, Any]:
    """Decrement room occupancy by 1."""
    conn = get_connection()
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(
            'UPDATE "Room" SET occupied = occupied - 1 WHERE id = %s RETURNING *',
            (room_id,)
        )
        room = dict(cursor.fetchone())
        conn.commit()
        cursor.close()
        return room
    except Exception as e:
        conn.rollback()
        raise Exception(f"Error decrementing room occupancy: {str(e)}")
    finally:
        conn.close()

