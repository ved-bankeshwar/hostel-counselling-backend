"""Script to create a clean room.py file."""

room_py_content = '''"""CRUD operations for Rooms model (denormalized)."""

import psycopg2
from psycopg2.extras import RealDictCursor
from typing import Optional, List, Dict, Any

DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "database": "room_counselling",
    "user": "admin",
    "password": "admin123"
}

def get_connection():
    """Create and return a database connection."""
    return psycopg2.connect(**DB_CONFIG)

def get_room_by_id(room_id: int) -> Optional[Dict[str, Any]]:
    """Get room by ID."""
    conn = get_connection()
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(\'''SELECT * FROM "Rooms" WHERE id = %s\''', (room_id,))
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
        query = \'''SELECT * FROM "Rooms"\'''
        params = []
        if filters:
            conditions = []
            for key, value in filters.items():
                conditions.append(f\'"{key}" = %s\')
                params.append(value)
            query += " WHERE " + " AND ".join(conditions)
        cursor.execute(query, params)
        rooms = [dict(row) for row in cursor.fetchall()]
        cursor.close()
        return rooms
    except Exception as e:
        raise Exception(f"Error fetching rooms: {str(e)}")
    finally:
        conn.close()

def create_room(data: Dict[str, Any]) -> Dict[str, Any]:
    """Create a new room."""
    conn = get_connection()
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(
            \'''INSERT INTO "Rooms" (
                "roomNumber", "floorNumber", "blockName", "isAC", "isDeluxe", 
                "isApartment", "hostelName", capacity, occupied
            ) VALUES (
                %(roomNumber)s, %(floorNumber)s, %(blockName)s, %(isAC)s, 
                %(isDeluxe)s, %(isApartment)s, %(hostelName)s, %(capacity)s, %(occupied)s
            ) RETURNING *\''',
            {
                "roomNumber": data["roomNumber"],
                "floorNumber": data["floorNumber"],
                "blockName": data["blockName"],
                "isAC": data.get("isAC", False),
                "isDeluxe": data.get("isDeluxe", False),
                "isApartment": data.get("isApartment", False),
                "hostelName": data["hostelName"],
                "capacity": data["capacity"],
                "occupied": data.get("occupied", 0),
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

def update_room(room_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
    """Update room by ID."""
    conn = get_connection()
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        set_clauses = []
        params = []
        for key, value in data.items():
            set_clauses.append(f\'"{key}" = %s\')
            params.append(value)
        params.append(room_id)
        query = f\'''UPDATE "Rooms" SET {", ".join(set_clauses)} WHERE id = %s RETURNING *\'''
        cursor.execute(query, params)
        room = cursor.fetchone()
        conn.commit()
        cursor.close()
        return dict(room) if room else None
    except Exception as e:
        conn.rollback()
        raise Exception(f"Error updating room: {str(e)}")
    finally:
        conn.close()

def delete_room(room_id: int) -> bool:
    """Delete room by ID."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(\'''DELETE FROM "Rooms" WHERE id = %s\''', (room_id,))
        deleted = cursor.rowcount > 0
        conn.commit()
        cursor.close()
        return deleted
    except Exception as e:
        conn.rollback()
        raise Exception(f"Error deleting room: {str(e)}")
    finally:
        conn.close()
'''

# Write the file
with open("dbconfig/room.py", "w", encoding="utf-8") as f:
    f.write(room_py_content)

print("✓ Created dbconfig/room.py successfully!")
