"""Check detailed hostel data structure."""
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
print("HOSTELS:")
print("=" * 80)
cur.execute('SELECT * FROM "Hostel" ORDER BY id')
for row in cur.fetchall():
    print(f"  [{row['id']}] {row['name']}")

print("\n" + "=" * 80)
print("BLOCKS (sample - first 6):")
print("=" * 80)
cur.execute('''
    SELECT b.*, h.name as hostel_name 
    FROM "Block" b 
    JOIN "Hostel" h ON b."hostelId" = h.id 
    ORDER BY b.id 
    LIMIT 6
''')
for row in cur.fetchall():
    features = []
    if row['isAC']: features.append('AC')
    if row['isDeluxe']: features.append('Deluxe')
    if row['isApartment']: features.append('Apartment')
    feature_str = ', '.join(features) if features else 'Standard'
    print(f"  [{row['id']}] {row['hostel_name']} - Block {row['blockName']} ({feature_str})")

print("\n" + "=" * 80)
print("FLOORS (sample - first 8):")
print("=" * 80)
cur.execute('''
    SELECT f.*, b."blockName", h.name as hostel_name
    FROM "Floor" f
    JOIN "Block" b ON f."blockId" = b.id
    JOIN "Hostel" h ON b."hostelId" = h.id
    ORDER BY f.id
    LIMIT 8
''')
for row in cur.fetchall():
    print(f"  [{row['id']}] {row['hostel_name']} Block {row['blockName']} - Floor {row['floorNumber']} (Rooms: {row['totalRooms']})")

print("\n" + "=" * 80)
print("ROOMS (sample - first 10):")
print("=" * 80)
cur.execute('''
    SELECT r.*, f."floorNumber", b."blockName", h.name as hostel_name
    FROM "Room" r
    JOIN "Floor" f ON r."floorId" = f.id
    JOIN "Block" b ON f."blockId" = b.id
    JOIN "Hostel" h ON b."hostelId" = h.id
    ORDER BY r.id
    LIMIT 10
''')
for row in cur.fetchall():
    status = f"Occupied: {row['occupied']}/{row['capacity']}"
    print(f"  [{row['id']}] {row['hostel_name']} Block {row['blockName']} Floor {row['floorNumber']} - Room {row['roomNumber']} (Cap: {row['capacity']}, {status})")

print("\n" + "=" * 80)
print("SUMMARY:")
print("=" * 80)
cur.execute('SELECT COUNT(*) FROM "Hostel"')
print(f"Total Hostels: {cur.fetchone()['count']}")

cur.execute('SELECT COUNT(*) FROM "Block"')
print(f"Total Blocks: {cur.fetchone()['count']}")

cur.execute('SELECT COUNT(*) FROM "Floor"')
print(f"Total Floors: {cur.fetchone()['count']}")

cur.execute('SELECT COUNT(*) FROM "Room"')
print(f"Total Rooms: {cur.fetchone()['count']}")

cur.execute('SELECT SUM(capacity) FROM "Room"')
print(f"Total Bed Capacity: {cur.fetchone()['sum']}")

cur.execute('SELECT SUM(occupied) FROM "Room"')
print(f"Total Occupied: {cur.fetchone()['sum']}")

cur.close()
conn.close()
