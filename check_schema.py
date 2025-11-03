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

# Check Rooms table
print("Rooms table columns:")
cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'Rooms' ORDER BY ordinal_position")
rooms_cols = [r['column_name'] for r in cur.fetchall()]
print(rooms_cols)

# Check one room record
cur.execute('SELECT * FROM "Rooms" LIMIT 1')
room = cur.fetchone()
print("\nSample room keys:", list(room.keys()) if room else "No rooms")

# Check Friendship table
print("\nFriendship table columns:")
cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'Friendship' ORDER BY ordinal_position")
friendship_cols = [r['column_name'] for r in cur.fetchall()]
print(friendship_cols)

# Check CounsellingSession table
print("\nCounsellingSession table columns:")
cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'CounsellingSession' ORDER BY ordinal_position")
session_cols = [r['column_name'] for r in cur.fetchall()]
print(session_cols)

conn.close()
