"""Debug room availability check."""
import psycopg2
from psycopg2.extras import RealDictCursor

conn = psycopg2.connect(
    host='localhost',
    port=5432,
    database='room_counselling',
    user='admin',
    password='admin123'
)

cur = conn.cursor(cursor_factory=RealDictCursor)

print("=" * 80)
print("ROOM AVAILABILITY DEBUG")
print("=" * 80)

# Get a specific room ID to check (replace with the room you're trying to select)
room_id = int(input("Enter room ID to check: "))

# Check the room details
cur.execute("""
    SELECT id, "roomNumber", "hostelName", "blockName", "floorNumber",
           capacity, occupied, "availableSlots", "isLocked",
           "assignedUserId", "assignedAt"
    FROM "Rooms"
    WHERE id = %s
""", (room_id,))

room = cur.fetchone()

if not room:
    print(f"\n❌ Room {room_id} NOT FOUND in database!")
else:
    print(f"\n✅ Room Found: {room['roomNumber']}")
    print(f"   Location: {room['hostelName']} - Block {room['blockName']} - Floor {room['floorNumber']}")
    print(f"\n📊 Availability Status:")
    print(f"   Capacity: {room['capacity']}")
    print(f"   Occupied: {room['occupied']}")
    print(f"   Available Slots: {room['availableSlots']}")
    print(f"   Is Locked: {room['isLocked']}")
    
    if room['assignedUserId']:
        print(f"\n👤 Assigned to User ID: {room['assignedUserId']}")
        print(f"   Assigned At: {room['assignedAt']}")
    else:
        print(f"\n👤 Not assigned to any user")
    
    print("\n🔍 Allocation Endpoint Checks:")
    
    # Check 1: Is locked?
    if room['isLocked']:
        print("   ❌ FAIL: Room is locked")
    else:
        print("   ✅ PASS: Room is not locked")
    
    # Check 2: Is full?
    if room['occupied'] >= room['capacity']:
        print(f"   ❌ FAIL: Room is full (occupied={room['occupied']}, capacity={room['capacity']})")
    else:
        print(f"   ✅ PASS: Room has space (occupied={room['occupied']}, capacity={room['capacity']})")
    
    # Overall verdict
    print("\n📋 Overall Verdict:")
    if not room['isLocked'] and room['occupied'] < room['capacity']:
        print("   ✅ Room SHOULD BE AVAILABLE for selection")
    else:
        print("   ❌ Room is NOT AVAILABLE")
        if room['isLocked']:
            print("      Reason: Room is locked")
        if room['occupied'] >= room['capacity']:
            print("      Reason: Room is full")

# Check if there are any available rooms
cur.execute("""
    SELECT COUNT(*) as count
    FROM "Rooms"
    WHERE "isLocked" = false AND occupied < capacity
""")
available_count = cur.fetchone()['count']
print(f"\n📊 Total Available Rooms in Database: {available_count}")

cur.close()
conn.close()
