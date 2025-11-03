import psycopg2
from psycopg2.extras import RealDictCursor

conn = psycopg2.connect(dbname='room_counselling', user='admin', password='admin123', host='localhost', port=5432)
cursor = conn.cursor(cursor_factory=RealDictCursor)

cursor.execute('SELECT COUNT(*) as count FROM "Rooms" WHERE "isLocked" = true')
print('Locked rooms:', cursor.fetchone()['count'])

cursor.execute('SELECT COUNT(*) as count FROM "Rooms" WHERE occupied >= capacity')
print('Full rooms:', cursor.fetchone()['count'])

cursor.execute('SELECT COUNT(*) as count FROM "Rooms" WHERE "isLocked" = false AND occupied < capacity')
print('Available rooms:', cursor.fetchone()['count'])

conn.close()
