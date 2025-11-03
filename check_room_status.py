import psycopg2
from psycopg2.extras import RealDictCursor
import sys

# Database configuration
DATABASE_CONFIG = {
    'dbname': 'room_counselling',
    'user': 'admin',
    'password': 'admin123',
    'host': 'localhost',
    'port': 5432
}

def check_room_status(room_id=None):
    """Check the status of a specific room or show sample available rooms"""
    try:
        conn = psycopg2.connect(**DATABASE_CONFIG)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        if room_id:
            # Check specific room
            cursor.execute("""
                SELECT id, "roomNumber", "hostelName", "blockName", "floorNumber",
                       capacity, occupied, "availableSlots", "isLocked", 
                       "assignedUserId", "assignedAt"
                FROM "Rooms"
                WHERE id = %s
            """, (room_id,))
            
            room = cursor.fetchone()
            
            if not room:
                print(f"\n❌ Room ID {room_id} not found in database!")
                return
            
            print(f"\n{'='*70}")
            print(f"ROOM STATUS FOR ID: {room_id}")
            print(f"{'='*70}")
            print(f"Room Number:     {room['roomNumber']}")
            print(f"Hostel:          {room['hostelName']}")
            print(f"Block:           {room['blockName']}")
            print(f"Floor:           {room['floorNumber']}")
            print(f"Capacity:        {room['capacity']}")
            print(f"Occupied:        {room['occupied']}")
            print(f"Available Slots: {room['availableSlots']}")
            print(f"Is Locked:       {room['isLocked']}")
            print(f"Assigned User:   {room['assignedUserId']}")
            print(f"Assigned At:     {room['assignedAt']}")
            print(f"{'='*70}\n")
            
            # Check availability conditions
            print("AVAILABILITY CHECKS:")
            print("-" * 70)
            
            # Check 1: Is locked?
            if room['isLocked']:
                print("❌ FAIL: Room is locked (isLocked = true)")
            else:
                print("✅ PASS: Room is not locked (isLocked = false)")
            
            # Check 2: Has available capacity?
            if room['occupied'] >= room['capacity']:
                print(f"❌ FAIL: Room is full (occupied {room['occupied']} >= capacity {room['capacity']})")
            else:
                print(f"✅ PASS: Room has space (occupied {room['occupied']} < capacity {room['capacity']})")
            
            # Overall verdict
            print("-" * 70)
            is_available = (not room['isLocked']) and (room['occupied'] < room['capacity'])
            if is_available:
                print("✅ VERDICT: Room SHOULD BE AVAILABLE for selection")
            else:
                print("❌ VERDICT: Room is NOT AVAILABLE for selection")
            print("-" * 70)
        
        else:
            # Show sample available rooms
            print("\n" + "="*70)
            print("SAMPLE AVAILABLE ROOMS (First 10)")
            print("="*70)
            
            cursor.execute("""
                SELECT id, "roomNumber", "hostelName", "floorNumber",
                       capacity, occupied, "isLocked"
                FROM "Rooms"
                WHERE "isLocked" = false AND occupied < capacity
                ORDER BY id
                LIMIT 10
            """)
            
            rooms = cursor.fetchall()
            
            if not rooms:
                print("❌ No available rooms found!")
            else:
                print(f"\nFound {len(rooms)} sample rooms:\n")
                for room in rooms:
                    print(f"ID: {room['id']:4d} | Room: {room['roomNumber']:6s} | "
                          f"Hostel: {room['hostelName'][:30]:30s} | Floor: {room['floorNumber']} | "
                          f"Occupied: {room['occupied']}/{room['capacity']}")
        
        # Count total available rooms
        cursor.execute("""
            SELECT COUNT(*) as count
            FROM "Rooms"
            WHERE "isLocked" = false AND occupied < capacity
        """)
        total = cursor.fetchone()['count']
        print(f"\nℹ️  Total available rooms in database: {total}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        try:
            room_id = int(sys.argv[1])
            check_room_status(room_id)
        except ValueError:
            print("Error: Room ID must be a number")
    else:
        check_room_status()
        print("\nUsage: python check_room_status.py [room_id]")
        print("Example: python check_room_status.py 1234")
