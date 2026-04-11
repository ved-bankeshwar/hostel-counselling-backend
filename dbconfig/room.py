import psycopg2
from psycopg2.extras import RealDictCursor
from typing import Optional, Dict, List, Any
import os

def get_db_config():
    """Get database configuration from environment variables"""
    database_url = os.getenv("DATABASE_URL")
    
    if database_url:
        from urllib.parse import urlparse
        result = urlparse(database_url)
        return {
            "host": result.hostname,
            "database": result.path[1:],
            "user": result.username,
            "password": result.password,
            "port": result.port or 5432
        }
    else:
        return {
            "host": os.getenv("DB_HOST", "localhost"),
            "database": os.getenv("DB_NAME", "room_counselling"),
            "user": os.getenv("DB_USER", "admin"),
            "password": os.getenv("DB_PASSWORD", "admin123"),
            "port": int(os.getenv("DB_PORT", "5432"))
        }

def get_connection():
    """Create and return a database connection"""
    return psycopg2.connect(**get_db_config())

def get_room_by_id(room_id: int) -> Optional[Dict]:
    """Get a single room by ID"""
    conn = get_connection()
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute('SELECT * FROM "Rooms" WHERE id = %s', (room_id,))
        room = cursor.fetchone()
        cursor.close()
        return dict(room) if room else None
    except Exception as e:
        raise Exception(f"Error fetching room: {str(e)}")
    finally:
        conn.close()

def get_all_rooms(filters: Optional[Dict] = None) -> List[Dict]:
    """Get all rooms with optional filters"""
    conn = get_connection()
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        query = 'SELECT * FROM "Rooms"'
        params = []
        
        if filters:
            conditions = []
            if 'hostelName' in filters:
                conditions.append('"hostelName" = %s')
                params.append(filters['hostelName'])
            if 'blockName' in filters:
                conditions.append('"blockName" = %s')
                params.append(filters['blockName'])
            if 'floorNumber' in filters:
                conditions.append('"floorNumber" = %s')
                params.append(filters['floorNumber'])
            if 'isAC' in filters:
                conditions.append('"isAC" = %s')
                params.append(filters['isAC'])
            if 'isDeluxe' in filters:
                conditions.append('"isDeluxe" = %s')
                params.append(filters['isDeluxe'])
            if 'isApartment' in filters:
                conditions.append('"isApartment" = %s')
                params.append(filters['isApartment'])
            if 'available' in filters and filters['available']:
                conditions.append('("capacity" - "occupied") > 0')
            if 'isLocked' in filters:
                conditions.append('"isLocked" = %s')
                params.append(filters['isLocked'])
                
            if conditions:
                query += ' WHERE ' + ' AND '.join(conditions)
        
        query += ' ORDER BY "hostelName", "blockName", "floorNumber", "roomNumber"'
        
        cursor.execute(query, params)
        rooms = [dict(row) for row in cursor.fetchall()]
        cursor.close()
        return rooms
    except Exception as e:
        raise Exception(f"Error fetching rooms: {str(e)}")
    finally:
        conn.close()

def create_room(data: Dict) -> Dict:
    """Create a new room"""
    conn = get_connection()
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        query = '''
            INSERT INTO "Rooms" (
                "roomNumber", "floorNumber", "blockName", "hostelName",
                "isAC", "isDeluxe", "isApartment", "capacity", "occupied"
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING *
        '''
        
        cursor.execute(query, (
            data.get('roomNumber'),
            data.get('floorNumber'),
            data.get('blockName'),
            data.get('hostelName'),
            data.get('isAC', False),
            data.get('isDeluxe', False),
            data.get('isApartment', False),
            data.get('capacity', 1),
            data.get('occupied', 0)
        ))
        
        room = cursor.fetchone()
        conn.commit()
        cursor.close()
        return dict(room)
    except Exception as e:
        conn.rollback()
        raise Exception(f"Error creating room: {str(e)}")
    finally:
        conn.close()

def update_room(room_id: int, data: Dict) -> Optional[Dict]:
    """Update an existing room"""
    conn = get_connection()
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        fields = []
        values = []
        
        updatable_fields = [
            'roomNumber', 'floorNumber', 'blockName', 'hostelName',
            'isAC', 'isDeluxe', 'isApartment', 'capacity', 'occupied',
            'assignedUserId', 'assignedAt', 'isLocked', 'lockedByUserId',
            'lockedAt', 'lockExpiresAt'
        ]
        
        for field in updatable_fields:
            if field in data:
                fields.append(f'"{field}" = %s')
                values.append(data[field])
        
        if not fields:
            return get_room_by_id(room_id)
        
        values.append(room_id)
        query = f'UPDATE "Rooms" SET {", ".join(fields)} WHERE id = %s RETURNING *'
        
        cursor.execute(query, values)
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
    """Delete a room"""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM "Rooms" WHERE id = %s', (room_id,))
        deleted = cursor.rowcount > 0
        conn.commit()
        cursor.close()
        return deleted
    except Exception as e:
        conn.rollback()
        raise Exception(f"Error deleting room: {str(e)}")
    finally:
        conn.close()

def get_all_hostels():
    """Get all distinct hostels with aggregated statistics"""
    conn = get_connection()
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        query = """
            SELECT DISTINCT "hostelName" as name,
                  COUNT(DISTINCT "blockName") as block_count,
                  COUNT(*) as room_count,
                  SUM(capacity) as total_capacity,
                  SUM(occupied) as total_occupied
           FROM "Rooms"
           GROUP BY "hostelName"
           ORDER BY "hostelName"
        """
        cursor.execute(query)
        hostels = [dict(row) for row in cursor.fetchall()]
        cursor.close()
        return hostels
    except Exception as e:
        raise Exception(f"Error fetching hostels: {str(e)}")
    finally:
        conn.close()

def get_blocks_by_hostel(hostel_name: str) -> List[Dict]:
    """Get all blocks in a specific hostel"""
    conn = get_connection()
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        query = """
            SELECT DISTINCT 
                "blockName" as name,
                "hostelName",
                COUNT(*) as room_count,
                SUM("capacity") as total_capacity,
                SUM("occupied") as total_occupied,
                SUM("capacity" - "occupied") as available_slots
            FROM "Rooms"
            WHERE "hostelName" = %s
            GROUP BY "blockName", "hostelName"
            ORDER BY "blockName"
        """
        cursor.execute(query, (hostel_name,))
        blocks = [dict(row) for row in cursor.fetchall()]
        cursor.close()
        return blocks
    except Exception as e:
        raise Exception(f"Error fetching blocks: {str(e)}")
    finally:
        conn.close()

def get_floors_by_hostel_and_block(hostel_name: str, block_name: str) -> List[Dict]:
    """Get all floors in a specific hostel and block"""
    conn = get_connection()
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        query = """
            SELECT DISTINCT 
                "floorNumber" as number,
                "blockName",
                "hostelName",
                COUNT(*) as room_count,
                SUM("capacity") as total_capacity,
                SUM("occupied") as total_occupied,
                SUM("capacity" - "occupied") as available_slots
            FROM "Rooms"
            WHERE "hostelName" = %s AND "blockName" = %s
            GROUP BY "floorNumber", "blockName", "hostelName"
            ORDER BY "floorNumber"
        """
        cursor.execute(query, (hostel_name, block_name))
        floors = [dict(row) for row in cursor.fetchall()]
        cursor.close()
        return floors
    except Exception as e:
        raise Exception(f"Error fetching floors: {str(e)}")
    finally:
        conn.close()

def assign_room(room_id: int, user_id: int) -> Optional[Dict]:
    """Assign a room to a user"""
    conn = get_connection()
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        cursor.execute(
            'SELECT "capacity", "occupied" FROM "Rooms" WHERE id = %s',
            (room_id,)
        )
        room_data = cursor.fetchone()
        
        if not room_data:
            cursor.close()
            conn.close()
            raise Exception("Room not found")
        
        if room_data['occupied'] >= room_data['capacity']:
            cursor.close()
            conn.close()
            raise Exception("Room is full")
        
        query = '''
            UPDATE "Rooms"
            SET "occupied" = "occupied" + 1,
                "assignedUserId" = %s,
                "assignedAt" = CURRENT_TIMESTAMP
            WHERE id = %s
            RETURNING *
        '''
        
        cursor.execute(query, (user_id, room_id))
        room = cursor.fetchone()
        conn.commit()
        cursor.close()
        return dict(room) if room else None
    except Exception as e:
        conn.rollback()
        raise Exception(f"Error assigning room: {str(e)}")
    finally:
        conn.close()

def lock_room(room_id: int, user_id: int, expires_at: Optional[str] = None) -> Optional[Dict]:
    """Lock a room for a user"""
    conn = get_connection()
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        cursor.execute(
            'SELECT "isLocked", "lockedByUserId" FROM "Rooms" WHERE id = %s',
            (room_id,)
        )
        room_data = cursor.fetchone()
        
        if not room_data:
            cursor.close()
            conn.close()
            raise Exception("Room not found")
        
        if room_data['isLocked'] and room_data['lockedByUserId'] != user_id:
            cursor.close()
            conn.close()
            raise Exception("Room is already locked by another user")
        
        query = '''
            UPDATE "Rooms"
            SET "isLocked" = true,
                "lockedByUserId" = %s,
                "lockedAt" = CURRENT_TIMESTAMP,
                "lockExpiresAt" = %s
            WHERE id = %s
            RETURNING *
        '''
        
        cursor.execute(query, (user_id, expires_at, room_id))
        room = cursor.fetchone()
        conn.commit()
        cursor.close()
        return dict(room) if room else None
    except Exception as e:
        conn.rollback()
        raise Exception(f"Error locking room: {str(e)}")
    finally:
        conn.close()

def unlock_room(room_id: int, user_id: Optional[int] = None) -> Optional[Dict]:
    """Unlock a room"""
    conn = get_connection()
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        cursor.execute(
            'SELECT "isLocked", "lockedByUserId" FROM "Rooms" WHERE id = %s',
            (room_id,)
        )
        room_data = cursor.fetchone()
        
        if not room_data:
            cursor.close()
            conn.close()
            raise Exception("Room not found")
        
        if not room_data['isLocked']:
            cursor.close()
            conn.close()
            raise Exception("Room is not locked")
        
        if user_id and room_data['lockedByUserId'] != user_id:
            cursor.close()
            conn.close()
            raise Exception("You don't have permission to unlock this room")
        
        query = '''
            UPDATE "Rooms"
            SET "isLocked" = false,
                "lockedByUserId" = NULL,
                "lockedAt" = NULL,
                "lockExpiresAt" = NULL
            WHERE id = %s
            RETURNING *
        '''
        
        cursor.execute(query, (room_id,))
        room = cursor.fetchone()
        conn.commit()
        cursor.close()
        return dict(room) if room else None
    except Exception as e:
        conn.rollback()
        raise Exception(f"Error unlocking room: {str(e)}")
    finally:
        conn.close()


def get_room_with_allocated_users(room_id: int) -> Optional[Dict]:
    """Get room details with list of all allocated users"""
    conn = get_connection()
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Get room details
        cursor.execute('SELECT * FROM "Rooms" WHERE id = %s', (room_id,))
        room = cursor.fetchone()
        
        if not room:
            cursor.close()
            conn.close()
            return None
        
        room_dict = dict(room)
        
        # Get all users allocated to this room
        cursor.execute("""
            SELECT u.id, u.name, u.email, u."registrationNumber", u.rank, u."allocatedAt"
            FROM "User" u
            WHERE u."allocatedRoomId" = %s
            ORDER BY u."allocatedAt" ASC
        """, (room_id,))
        
        allocated_users = [dict(row) for row in cursor.fetchall()]
        room_dict['allocatedUsers'] = allocated_users
        
        cursor.close()
        return room_dict
    except Exception as e:
        raise Exception(f"Error fetching room with allocated users: {str(e)}")
    finally:
        conn.close()


def get_all_rooms_with_allocations() -> List[Dict]:
    """Get all rooms with their allocated users"""
    conn = get_connection()
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Get all rooms
        cursor.execute("""
            SELECT * FROM "Rooms"
            ORDER BY "hostelName", "blockName", "floorNumber", "roomNumber"
        """)
        rooms = [dict(row) for row in cursor.fetchall()]
        
        # For each room, get allocated users
        for room in rooms:
            cursor.execute("""
                SELECT u.id, u.name, u.email, u."registrationNumber", u.rank, u."allocatedAt"
                FROM "User" u
                WHERE u."allocatedRoomId" = %s
                ORDER BY u."allocatedAt" ASC
            """, (room['id'],))
            
            room['allocatedUsers'] = [dict(row) for row in cursor.fetchall()]
        
        cursor.close()
        return rooms
    except Exception as e:
        raise Exception(f"Error fetching rooms with allocations: {str(e)}")
    finally:
        conn.close()


def increment_room_occupancy(room_id: int) -> Optional[Dict]:
    """Increment the occupied count for a room"""
    conn = get_connection()
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("""
            UPDATE "Rooms"
            SET occupied = occupied + 1
            WHERE id = %s
            RETURNING *
        """, (room_id,))
        room = cursor.fetchone()
        conn.commit()
        cursor.close()
        return dict(room) if room else None
    except Exception as e:
        conn.rollback()
        raise Exception(f"Error incrementing room occupancy: {str(e)}")
    finally:
        conn.close()


def decrement_room_occupancy(room_id: int) -> Optional[Dict]:
    """Decrement the occupied count for a room"""
    conn = get_connection()
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("""
            UPDATE "Rooms"
            SET occupied = GREATEST(occupied - 1, 0)
            WHERE id = %s
            RETURNING *
        """, (room_id,))
        room = cursor.fetchone()
        conn.commit()
        cursor.close()
        return dict(room) if room else None
    except Exception as e:
        conn.rollback()
        raise Exception(f"Error decrementing room occupancy: {str(e)}")
    finally:
        conn.close()
