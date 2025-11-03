"""Script to append hostel/block/floor functions to room.py."""

additional_functions = '''
def get_all_hostels() -> List[Dict[str, Any]]:
    """Get all unique hostels from the Rooms table."""
    conn = get_connection()
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(
            \'''SELECT DISTINCT "hostelName" as name,
                      COUNT(DISTINCT "blockName") as block_count,
                      COUNT(*) as room_count,
                      SUM(capacity) as total_capacity,
                      SUM(occupied) as total_occupied
               FROM "Rooms"
               GROUP BY "hostelName"
               ORDER BY "hostelName"\'''
        )
        hostels = [dict(row) for row in cursor.fetchall()]
        cursor.close()
        return hostels
    except Exception as e:
        raise Exception(f"Error fetching hostels: {str(e)}")
    finally:
        conn.close()


def get_hostel_by_name(hostel_name: str) -> Optional[Dict[str, Any]]:
    """Get hostel details by name."""
    conn = get_connection()
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(
            \'''SELECT "hostelName" as name,
                      COUNT(DISTINCT "blockName") as block_count,
                      COUNT(*) as room_count,
                      SUM(capacity) as total_capacity,
                      SUM(occupied) as total_occupied,
                      SUM("availableSlots") as available_slots
               FROM "Rooms"
               WHERE "hostelName" = %s
               GROUP BY "hostelName"\''',
            (hostel_name,)
        )
        hostel = cursor.fetchone()
        cursor.close()
        return dict(hostel) if hostel else None
    except Exception as e:
        raise Exception(f"Error fetching hostel: {str(e)}")
    finally:
        conn.close()


def get_all_blocks(hostel_name: Optional[str] = None) -> List[Dict[str, Any]]:
    """Get all unique blocks, optionally filtered by hostel."""
    conn = get_connection()
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        query = \'''SELECT DISTINCT "hostelName", "blockName", "isAC", "isDeluxe", "isApartment",
                          COUNT(*) as room_count,
                          SUM(capacity) as total_capacity,
                          SUM(occupied) as total_occupied,
                          SUM("availableSlots") as available_slots
                   FROM "Rooms"\'''
        params = []
        if hostel_name:
            query += ''' WHERE "hostelName" = %s\'''
            params.append(hostel_name)
        query += ''' GROUP BY "hostelName", "blockName", "isAC", "isDeluxe", "isApartment" ORDER BY "hostelName", "blockName"\'''
        cursor.execute(query, params)
        blocks = [dict(row) for row in cursor.fetchall()]
        cursor.close()
        return blocks
    except Exception as e:
        raise Exception(f"Error fetching blocks: {str(e)}")
    finally:
        conn.close()


def get_all_floors(hostel_name: Optional[str] = None, block_name: Optional[str] = None) -> List[Dict[str, Any]]:
    """Get all unique floors, optionally filtered by hostel and/or block."""
    conn = get_connection()
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        query = \'''SELECT DISTINCT "hostelName", "blockName", "floorNumber",
                          COUNT(*) as room_count,
                          SUM(capacity) as total_capacity,
                          SUM(occupied) as total_occupied,
                          SUM("availableSlots") as available_slots
                   FROM "Rooms"
                   WHERE 1=1\'''
        params = []
        if hostel_name:
            query += ''' AND "hostelName" = %s\'''
            params.append(hostel_name)
        if block_name:
            query += ''' AND "blockName" = %s\'''
            params.append(block_name)
        query += ''' GROUP BY "hostelName", "blockName", "floorNumber" ORDER BY "hostelName", "blockName", "floorNumber"\'''
        cursor.execute(query, params)
        floors = [dict(row) for row in cursor.fetchall()]
        cursor.close()
        return floors
    except Exception as e:
        raise Exception(f"Error fetching floors: {str(e)}")
    finally:
        conn.close()
'''

# Append to existing room.py
with open("dbconfig/room.py", "a", encoding="utf-8") as f:
    f.write(additional_functions)

print("✓ Added hostel/block/floor functions to room.py!")
