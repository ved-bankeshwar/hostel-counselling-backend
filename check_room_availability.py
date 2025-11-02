"""Quick reference for checking available rooms."""
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
print("ROOM AVAILABILITY SUMMARY")
print("=" * 80)

# Available rooms by hostel
cur.execute('''
    SELECT h.name as hostel, 
           COUNT(r.id) as total_rooms,
           SUM(r.capacity) as total_capacity,
           SUM(r.occupied) as occupied,
           SUM(r.capacity - r.occupied) as available
    FROM "Hostel" h
    JOIN "Block" b ON h.id = b."hostelId"
    JOIN "Floor" f ON b.id = f."blockId"
    JOIN "Room" r ON f.id = r."floorId"
    GROUP BY h.id, h.name
    ORDER BY h.name
''')

print("\nBy Hostel:")
total_rooms = 0
total_capacity = 0
total_occupied = 0
total_available = 0

for row in cur.fetchall():
    print(f"\n  {row['hostel']}")
    print(f"    Rooms: {row['total_rooms']}")
    print(f"    Capacity: {row['total_capacity']} beds")
    print(f"    Occupied: {row['occupied']} beds")
    print(f"    Available: {row['available']} beds")
    
    total_rooms += row['total_rooms']
    total_capacity += row['total_capacity']
    total_occupied += row['occupied']
    total_available += row['available']

print("\n" + "-" * 80)
print("TOTALS:")
print(f"  Total Rooms: {total_rooms}")
print(f"  Total Capacity: {total_capacity} beds")
print(f"  Occupied: {total_occupied} beds ({total_occupied/total_capacity*100:.1f}%)")
print(f"  Available: {total_available} beds ({total_available/total_capacity*100:.1f}%)")

# Completely empty rooms
cur.execute('''
    SELECT COUNT(*) as count
    FROM "Room"
    WHERE occupied = 0
''')
empty_rooms = cur.fetchone()['count']
print(f"\n  Completely Empty Rooms: {empty_rooms}")

# Partially filled rooms
cur.execute('''
    SELECT COUNT(*) as count
    FROM "Room"
    WHERE occupied > 0 AND occupied < capacity
''')
partial_rooms = cur.fetchone()['count']
print(f"  Partially Filled Rooms: {partial_rooms}")

# Full rooms
cur.execute('''
    SELECT COUNT(*) as count
    FROM "Room"
    WHERE occupied = capacity
''')
full_rooms = cur.fetchone()['count']
print(f"  Full Rooms: {full_rooms}")

print("=" * 80)

cur.close()
conn.close()
