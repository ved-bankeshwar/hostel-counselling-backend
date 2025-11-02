"""
Comprehensive script to add/update sample hostel data.
This script adds realistic hostel, block, floor, and room data.
"""

import psycopg2
from psycopg2.extras import RealDictCursor

# Database connection
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'room_counselling',
    'user': 'admin',
    'password': 'admin123'
}

def get_connection():
    return psycopg2.connect(**DB_CONFIG)


def clear_existing_data(conn):
    """Clear existing hostel data (optional - use with caution!)."""
    cursor = conn.cursor()
    
    print("⚠️  WARNING: This will delete all existing hostel data!")
    response = input("Do you want to proceed? (yes/no): ")
    
    if response.lower() != 'yes':
        print("Aborted. Keeping existing data.")
        return False
    
    print("\nClearing existing data...")
    
    # Delete in reverse order of dependencies
    cursor.execute('DELETE FROM "RoomAssignment"')
    cursor.execute('DELETE FROM "Preference"')
    cursor.execute('DELETE FROM "Room"')
    cursor.execute('DELETE FROM "Floor"')
    cursor.execute('DELETE FROM "Block"')
    cursor.execute('DELETE FROM "Hostel"')
    
    conn.commit()
    cursor.close()
    print("✓ Existing data cleared\n")
    return True


def add_hostels(conn):
    """Add hostel buildings."""
    cursor = conn.cursor()
    
    hostels = [
        # Men's Hostels
        "Vivekananda Hostel (Men)",
        "Ramanujan Hostel (Men)",
        "Tagore Hostel (Men)",
        "APJ Abdul Kalam Hostel (Men)",
        
        # Women's Hostels
        "Sarojini Naidu Hostel (Women)",
        "Indira Gandhi Hostel (Women)",
        "Rani Lakshmibai Hostel (Women)",
    ]
    
    for name in hostels:
        cursor.execute(
            'INSERT INTO "Hostel" (name) VALUES (%s) ON CONFLICT (name) DO NOTHING RETURNING id',
            (name,)
        )
        result = cursor.fetchone()
        if result:
            print(f"  + Added hostel: {name}")
    
    conn.commit()
    cursor.close()
    print(f"✓ Added {len(hostels)} hostels\n")


def add_blocks(conn):
    """Add blocks to hostels with different configurations."""
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    # Get all hostels
    cursor.execute('SELECT id, name FROM "Hostel" ORDER BY id')
    hostels = cursor.fetchall()
    
    block_configs = [
        # (blockName, isAC, isDeluxe, isApartment, description)
        ('A', False, False, False, 'Standard Non-AC'),
        ('B', True, False, False, 'AC Standard'),
        ('C', True, True, False, 'AC Deluxe'),
        ('D', True, True, True, 'AC Apartment Style'),
    ]
    
    added_count = 0
    for hostel in hostels:
        hostel_id = hostel['id']
        hostel_name = hostel['name']
        
        # Add 3-4 blocks per hostel
        num_blocks = 3 if 'Women' in hostel_name else 4
        
        for i in range(num_blocks):
            block_name, is_ac, is_deluxe, is_apartment, desc = block_configs[i]
            
            cursor.execute('''
                INSERT INTO "Block" ("hostelId", "blockName", "isAC", "isDeluxe", "isApartment")
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT DO NOTHING
                RETURNING id
            ''', (hostel_id, block_name, is_ac, is_deluxe, is_apartment))
            
            result = cursor.fetchone()
            if result:
                print(f"  + {hostel_name} - Block {block_name} ({desc})")
                added_count += 1
    
    conn.commit()
    cursor.close()
    print(f"✓ Added {added_count} blocks\n")


def add_floors(conn):
    """Add floors to blocks."""
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    # Get all blocks
    cursor.execute('''
        SELECT b.id, b."blockName", h.name as hostel_name, b."isApartment"
        FROM "Block" b
        JOIN "Hostel" h ON b."hostelId" = h.id
        ORDER BY b.id
    ''')
    blocks = cursor.fetchall()
    
    added_count = 0
    for block in blocks:
        block_id = block['id']
        block_name = block['blockName']
        hostel_name = block['hostel_name']
        is_apartment = block['isApartment']
        
        # Apartments have fewer rooms per floor
        rooms_per_floor = 20 if is_apartment else 40
        
        # Add 4-6 floors per block
        num_floors = 4 if is_apartment else 5
        
        for floor_num in range(1, num_floors + 1):
            cursor.execute('''
                INSERT INTO "Floor" ("blockId", "floorNumber", "totalRooms")
                VALUES (%s, %s, %s)
                ON CONFLICT DO NOTHING
                RETURNING id
            ''', (block_id, floor_num, rooms_per_floor))
            
            result = cursor.fetchone()
            if result:
                added_count += 1
    
    conn.commit()
    cursor.close()
    print(f"✓ Added {added_count} floors")


def add_rooms(conn):
    """Add rooms to floors with varying capacities."""
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    # Get all floors with block information
    cursor.execute('''
        SELECT f.id as floor_id, f."floorNumber", f."totalRooms",
               b."blockName", b."isAC", b."isDeluxe", b."isApartment",
               h.name as hostel_name
        FROM "Floor" f
        JOIN "Block" b ON f."blockId" = b.id
        JOIN "Hostel" h ON b."hostelId" = h.id
        ORDER BY f.id
    ''')
    floors = cursor.fetchall()
    
    added_count = 0
    total_capacity = 0
    
    for floor in floors:
        floor_id = floor['floor_id']
        floor_num = floor['floorNumber']
        total_rooms = floor['totalRooms']
        is_apartment = floor['isApartment']
        is_deluxe = floor['isDeluxe']
        
        # Room numbering: FloorNum + RoomNum (e.g., Floor 1 Room 5 = 105)
        base_room_num = floor_num * 100
        
        # Determine room capacity distribution
        # Capacity must be between 2 and 6 (as per DB constraint)
        if is_apartment:
            # Apartments: Mostly doubles and triples
            capacities = [2, 2, 2, 3, 3, 4]
        elif is_deluxe:
            # Deluxe: Mostly doubles and triples
            capacities = [2, 2, 2, 3, 3, 3, 4, 4]
        else:
            # Standard: Mix of all types, more triples and quads
            capacities = [2, 2, 3, 3, 3, 4, 4, 4]
        
        # Generate rooms
        for i in range(1, total_rooms + 1):
            room_number = str(base_room_num + i)
            
            # Cycle through capacity types
            capacity = capacities[i % len(capacities)]
            
            cursor.execute('''
                INSERT INTO "Room" ("floorId", "roomNumber", capacity, occupied)
                VALUES (%s, %s, %s, 0)
                ON CONFLICT DO NOTHING
                RETURNING id
            ''', (floor_id, room_number, capacity))
            
            result = cursor.fetchone()
            if result:
                added_count += 1
                total_capacity += capacity
    
    conn.commit()
    cursor.close()
    print(f"✓ Added {added_count} rooms (Total capacity: {total_capacity} beds)\n")


def print_summary(conn):
    """Print summary of hostel data."""
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    print("=" * 80)
    print("HOSTEL DATA SUMMARY")
    print("=" * 80)
    
    # List all hostels
    cursor.execute('SELECT id, name FROM "Hostel" ORDER BY id')
    print("\nHostels:")
    for row in cursor.fetchall():
        print(f"  [{row['id']}] {row['name']}")
    
    # Count blocks by type
    cursor.execute('''
        SELECT 
            CASE 
                WHEN "isApartment" THEN 'Apartment'
                WHEN "isDeluxe" THEN 'Deluxe'
                WHEN "isAC" THEN 'AC Standard'
                ELSE 'Standard'
            END as block_type,
            COUNT(*) as count
        FROM "Block"
        GROUP BY block_type
        ORDER BY count DESC
    ''')
    print("\nBlocks by Type:")
    for row in cursor.fetchall():
        print(f"  {row['block_type']}: {row['count']}")
    
    # Total counts
    cursor.execute('SELECT COUNT(*) as count FROM "Hostel"')
    hostel_count = cursor.fetchone()['count']
    
    cursor.execute('SELECT COUNT(*) as count FROM "Block"')
    block_count = cursor.fetchone()['count']
    
    cursor.execute('SELECT COUNT(*) as count FROM "Floor"')
    floor_count = cursor.fetchone()['count']
    
    cursor.execute('SELECT COUNT(*) as count FROM "Room"')
    room_count = cursor.fetchone()['count']
    
    cursor.execute('SELECT SUM(capacity) as total FROM "Room"')
    total_capacity = cursor.fetchone()['total']
    
    cursor.execute('SELECT SUM(occupied) as total FROM "Room"')
    occupied = cursor.fetchone()['total'] or 0
    
    # Room distribution by capacity
    cursor.execute('''
        SELECT capacity, COUNT(*) as count
        FROM "Room"
        GROUP BY capacity
        ORDER BY capacity
    ''')
    print("\nRooms by Capacity:")
    for row in cursor.fetchall():
        room_type = {2: 'Double', 3: 'Triple', 4: 'Quad', 5: 'Five-bed', 6: 'Six-bed'}.get(row['capacity'], f"{row['capacity']}-bed")
        print(f"  {room_type}: {row['count']} rooms")
    
    print("\nOverall Statistics:")
    print(f"  Total Hostels: {hostel_count}")
    print(f"  Total Blocks: {block_count}")
    print(f"  Total Floors: {floor_count}")
    print(f"  Total Rooms: {room_count}")
    print(f"  Total Bed Capacity: {total_capacity}")
    print(f"  Currently Occupied: {occupied}")
    print(f"  Available Beds: {total_capacity - occupied}")
    
    cursor.close()
    print("=" * 80)


def main():
    """Main function to orchestrate data loading."""
    print("\n" + "=" * 80)
    print("HOSTEL DATA LOADER")
    print("=" * 80)
    print("\nThis script will add sample hostel, block, floor, and room data.")
    print("It will NOT delete existing data unless you explicitly choose to.\n")
    
    conn = get_connection()
    
    try:
        # Optional: Clear existing data
        # Uncomment the line below if you want to offer data clearing
        # clear_existing_data(conn)
        
        print("Adding hostel data...\n")
        
        # Add data in order of dependencies
        add_hostels(conn)
        add_blocks(conn)
        add_floors(conn)
        add_rooms(conn)
        
        # Print summary
        print_summary(conn)
        
        print("\n✅ Hostel data loaded successfully!")
        
    except Exception as e:
        conn.rollback()
        print(f"\n❌ Error: {e}")
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    main()
