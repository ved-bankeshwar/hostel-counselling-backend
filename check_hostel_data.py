"""Check current data in hostel-related tables."""
import psycopg2

conn = psycopg2.connect(
    host='localhost',
    port=5432,
    database='room_counselling',
    user='admin',
    password='admin123'
)

cur = conn.cursor()

tables = ['Hostel', 'Block', 'Floor', 'Room']
for table in tables:
    cur.execute(f'SELECT COUNT(*) FROM "{table}"')
    count = cur.fetchone()[0]
    print(f'{table}: {count} records')

cur.close()
conn.close()
