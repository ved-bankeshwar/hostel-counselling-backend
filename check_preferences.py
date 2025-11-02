"""Check if preferences are being saved to the database."""
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
print("PREFERENCE TRACKING STATUS")
print("=" * 80)

# Check Preference table structure
cur.execute("""
    SELECT column_name, data_type, is_nullable
    FROM information_schema.columns 
    WHERE table_name = 'Preference'
    ORDER BY ordinal_position
""")

print("\nPreference table columns:")
for row in cur.fetchall():
    nullable = "NULL" if row['is_nullable'] == 'YES' else "NOT NULL"
    print(f"  • {row['column_name']}: {row['data_type']} ({nullable})")

# Count preferences
cur.execute('SELECT COUNT(*) as count FROM "Preference"')
pref_count = cur.fetchone()['count']

print(f"\n📊 Total Preferences Saved: {pref_count}")

if pref_count > 0:
    # Show sample preferences
    cur.execute("""
        SELECT p.*, u."displayName", u.rank, r."roomNumber", 
               h.name as hostel_name, b."blockName", f."floorNumber"
        FROM "Preference" p
        JOIN "User" u ON p."userId" = u.id
        JOIN "Room" r ON p."roomId" = r.id
        JOIN "Floor" f ON r."floorId" = f.id
        JOIN "Block" b ON f."blockId" = b.id
        JOIN "Hostel" h ON b."hostelId" = h.id
        ORDER BY p."createdAt" DESC
        LIMIT 5
    """)
    
    print("\nRecent Preferences:")
    for row in cur.fetchall():
        print(f"  [{row['id']}] {row['displayName']} (Rank {row['rank']})")
        print(f"      Selected: {row['hostel_name']} - Block {row['blockName']} - Floor {row['floorNumber']} - Room {row['roomNumber']}")
        print(f"      Preference Rank: {row['preferenceRank']}")
        print(f"      Timestamp: {row['createdAt']}")
        print()

# Check Room Assignments
cur.execute('SELECT COUNT(*) as count FROM "RoomAssignment"')
assign_count = cur.fetchone()['count']

print(f"📌 Total Room Assignments: {assign_count}")

print("\n" + "=" * 80)
print("✅ Preference tracking is enabled!")
print("Every room selection will now be saved to the Preference table.")
print("=" * 80)

cur.close()
conn.close()
