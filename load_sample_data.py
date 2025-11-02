"""Script to load sample data into the PostgreSQL database."""

import psycopg2
from psycopg2.extras import execute_values
from datetime import datetime
import bcrypt

# Database connection parameters
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'room_counselling',
    'user': 'admin',
    'password': 'admin123'
}


def get_connection():
    """Create and return a database connection."""
    return psycopg2.connect(**DB_CONFIG)


def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def create_tables(conn):
    """Create all necessary tables if they don't exist."""
    cursor = conn.cursor()
    
    # Create enum types
    cursor.execute("""
        DO $$ BEGIN
            CREATE TYPE "Gender" AS ENUM ('male', 'female');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)
    
    cursor.execute("""
        DO $$ BEGIN
            CREATE TYPE "HostelType" AS ENUM ('mens', 'ladies');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)
    
    cursor.execute("""
        DO $$ BEGIN
            CREATE TYPE "FriendStatus" AS ENUM ('pending', 'accepted', 'rejected');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)
    
    # Create User table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS "User" (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            email VARCHAR(255) UNIQUE NOT NULL,
            "passwordHash" VARCHAR(255),
            "registrationNumber" VARCHAR(255) UNIQUE,
            gender "Gender" NOT NULL,
            rank INTEGER UNIQUE NOT NULL,
            hostel "HostelType" NOT NULL,
            "isActive" BOOLEAN DEFAULT true,
            "createdAt" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            "firebaseUid" VARCHAR(255) UNIQUE,
            "displayName" VARCHAR(255),
            "photoUrl" TEXT,
            "provider" VARCHAR(50) DEFAULT 'google',
            "lastLoginAt" TIMESTAMP,
            "updatedAt" TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_rank ON \"User\"(rank);")
    
    # Create Friendship table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS "Friendship" (
            id SERIAL PRIMARY KEY,
            "userId" INTEGER NOT NULL REFERENCES "User"(id) ON DELETE CASCADE,
            "friendId" INTEGER NOT NULL REFERENCES "User"(id) ON DELETE CASCADE,
            status "FriendStatus" NOT NULL,
            "createdAt" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE("userId", "friendId")
        );
    """)
    
    # Create Hostel table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS "Hostel" (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255) UNIQUE NOT NULL
        );
    """)
    
    # Create Block table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS "Block" (
            id SERIAL PRIMARY KEY,
            "hostelId" INTEGER NOT NULL REFERENCES "Hostel"(id) ON DELETE CASCADE,
            "blockName" VARCHAR(255) NOT NULL,
            "isAC" BOOLEAN NOT NULL,
            "isDeluxe" BOOLEAN NOT NULL,
            "isApartment" BOOLEAN NOT NULL,
            UNIQUE("hostelId", "blockName")
        );
    """)
    
    # Create Floor table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS "Floor" (
            id SERIAL PRIMARY KEY,
            "blockId" INTEGER NOT NULL REFERENCES "Block"(id) ON DELETE CASCADE,
            "floorNumber" INTEGER NOT NULL,
            "totalRooms" INTEGER DEFAULT 40,
            UNIQUE("blockId", "floorNumber")
        );
    """)
    
    # Create Room table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS "Room" (
            id SERIAL PRIMARY KEY,
            "floorId" INTEGER NOT NULL REFERENCES "Floor"(id) ON DELETE CASCADE,
            "roomNumber" VARCHAR(255) NOT NULL,
            capacity INTEGER NOT NULL CHECK (capacity >= 2 AND capacity <= 6),
            occupied INTEGER DEFAULT 0,
            UNIQUE("floorId", "roomNumber")
        );
    """)
    
    # Create Preference table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS "Preference" (
            id SERIAL PRIMARY KEY,
            "userId" INTEGER NOT NULL REFERENCES "User"(id) ON DELETE CASCADE,
            "preferenceRank" INTEGER NOT NULL CHECK ("preferenceRank" >= 1 AND "preferenceRank" <= 5),
            "roomId" INTEGER NOT NULL REFERENCES "Room"(id) ON DELETE CASCADE,
            "createdAt" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE("userId", "preferenceRank")
        );
    """)
    
    # Create RoomAssignment table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS "RoomAssignment" (
            id SERIAL PRIMARY KEY,
            "roomId" INTEGER NOT NULL REFERENCES "Room"(id) ON DELETE CASCADE,
            "userId" INTEGER NOT NULL REFERENCES "User"(id) ON DELETE CASCADE,
            "groupId" VARCHAR(255) DEFAULT gen_random_uuid()::text,
            "assignedAt" TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_room_assignment_group ON \"RoomAssignment\"(\"groupId\");")
    
    conn.commit()
    cursor.close()
    print("✓ Tables created successfully")


def load_hostels(conn):
    """Load sample hostel data."""
    cursor = conn.cursor()
    
    hostels = [
        ("Mens Hostel Block A",),
        ("Mens Hostel Block B",),
        ("Ladies Hostel Block A",),
        ("Ladies Hostel Block B",),
    ]
    
    cursor.executemany(
        'INSERT INTO "Hostel" (name) VALUES (%s) ON CONFLICT (name) DO NOTHING',
        hostels
    )
    
    conn.commit()
    cursor.close()
    print(f"✓ Loaded {len(hostels)} hostels")


def load_blocks(conn):
    """Load sample block data."""
    cursor = conn.cursor()
    
    # Get hostel IDs
    cursor.execute('SELECT id, name FROM "Hostel" ORDER BY id')
    hostels = cursor.fetchall()
    
    blocks = []
    for hostel_id, hostel_name in hostels:
        # Create 2-3 blocks per hostel with different configurations
        blocks.extend([
            (hostel_id, 'A', False, False, False),  # Non-AC, Standard
            (hostel_id, 'B', True, False, False),   # AC, Standard
            (hostel_id, 'C', True, True, False),    # AC, Deluxe
        ])
    
    cursor.executemany(
        'INSERT INTO "Block" ("hostelId", "blockName", "isAC", "isDeluxe", "isApartment") VALUES (%s, %s, %s, %s, %s) ON CONFLICT DO NOTHING',
        blocks
    )
    
    conn.commit()
    cursor.close()
    print(f"✓ Loaded {len(blocks)} blocks")


def load_floors(conn):
    """Load sample floor data."""
    cursor = conn.cursor()
    
    # Get all block IDs
    cursor.execute('SELECT id FROM "Block"')
    blocks = cursor.fetchall()
    
    floors = []
    for (block_id,) in blocks:
        # Create 4 floors per block
        for floor_num in range(1, 5):
            floors.append((block_id, floor_num, 40))
    
    cursor.executemany(
        'INSERT INTO "Floor" ("blockId", "floorNumber", "totalRooms") VALUES (%s, %s, %s) ON CONFLICT DO NOTHING',
        floors
    )
    
    conn.commit()
    cursor.close()
    print(f"✓ Loaded {len(floors)} floors")


def load_rooms(conn):
    """Load sample room data."""
    cursor = conn.cursor()
    
    # Get all floor IDs
    cursor.execute('SELECT id FROM "Floor"')
    floors = cursor.fetchall()
    
    rooms = []
    for (floor_id,) in floors:
        # Create 10 rooms per floor with varying capacities
        for room_num in range(101, 111):
            # Alternate between different capacities
            capacity = 2 if room_num % 3 == 0 else (3 if room_num % 2 == 0 else 4)
            rooms.append((floor_id, str(room_num), capacity, 0))
    
    cursor.executemany(
        'INSERT INTO "Room" ("floorId", "roomNumber", capacity, occupied) VALUES (%s, %s, %s, %s) ON CONFLICT DO NOTHING',
        rooms
    )
    
    conn.commit()
    cursor.close()
    print(f"✓ Loaded {len(rooms)} rooms")


def load_users(conn):
    """Load sample user data with Firebase UIDs."""
    cursor = conn.cursor()
    
    users = []
    # Create 30 male students with fake Firebase UIDs for testing
    for i in range(1, 31):
        users.append((
            f"firebase_test_male_{i}",  # firebaseUid (fake for testing)
            f"male.student{i}@example.com",
            f"Male Student {i}",  # displayName
            f"MS2024{str(i).zfill(4)}",  # registrationNumber
            'male',
            i,
            'mens',
            True
        ))
    
    # Create 30 female students with fake Firebase UIDs for testing
    for i in range(1, 31):
        users.append((
            f"firebase_test_female_{i}",  # firebaseUid (fake for testing)
            f"female.student{i}@example.com",
            f"Female Student {i}",  # displayName
            f"FS2024{str(i).zfill(4)}",  # registrationNumber
            'female',
            i + 30,
            'ladies',
            True
        ))
    
    cursor.executemany(
        '''INSERT INTO "User" (
            "firebaseUid", email, "displayName", "registrationNumber", gender, rank, hostel, "isActive"
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s) ON CONFLICT DO NOTHING''',
        users
    )
    
    conn.commit()
    cursor.close()
    print(f"✓ Loaded {len(users)} users")


def load_friendships(conn):
    """Load sample friendship data."""
    cursor = conn.cursor()
    
    # Get all user IDs
    cursor.execute('SELECT id FROM "User" ORDER BY id LIMIT 20')
    users = [row[0] for row in cursor.fetchall()]
    
    friendships = []
    # Create some friendships between users
    for i in range(0, len(users) - 1, 2):
        if i + 1 < len(users):
            friendships.append((users[i], users[i + 1], 'accepted'))
    
    # Add some pending friendships
    for i in range(2, min(10, len(users))):
        if i - 2 >= 0:
            friendships.append((users[i], users[i - 2], 'pending'))
    
    cursor.executemany(
        'INSERT INTO "Friendship" ("userId", "friendId", status) VALUES (%s, %s, %s) ON CONFLICT DO NOTHING',
        friendships
    )
    
    conn.commit()
    cursor.close()
    print(f"✓ Loaded {len(friendships)} friendships")


def load_preferences(conn):
    """Load sample preference data."""
    cursor = conn.cursor()
    
    # Get first 15 users
    cursor.execute('SELECT id FROM "User" ORDER BY id LIMIT 15')
    users = [row[0] for row in cursor.fetchall()]
    
    # Get some rooms
    cursor.execute('SELECT id FROM "Room" ORDER BY id LIMIT 25')
    rooms = [row[0] for row in cursor.fetchall()]
    
    preferences = []
    for user_id in users:
        # Each user sets 5 preferences
        for rank in range(1, 6):
            room_idx = (user_id * 5 + rank - 1) % len(rooms)
            preferences.append((user_id, rank, rooms[room_idx]))
    
    cursor.executemany(
        'INSERT INTO "Preference" ("userId", "preferenceRank", "roomId") VALUES (%s, %s, %s) ON CONFLICT DO NOTHING',
        preferences
    )
    
    conn.commit()
    cursor.close()
    print(f"✓ Loaded {len(preferences)} preferences")


def load_room_assignments(conn):
    """Load sample room assignment data."""
    cursor = conn.cursor()
    
    # Get first 10 users
    cursor.execute('SELECT id FROM "User" ORDER BY id LIMIT 10')
    users = [row[0] for row in cursor.fetchall()]
    
    # Get some rooms
    cursor.execute('SELECT id FROM "Room" ORDER BY id LIMIT 5')
    rooms = [row[0] for row in cursor.fetchall()]
    
    assignments = []
    import uuid
    
    # Assign 2 users per room
    for i in range(0, len(users), 2):
        if i + 1 < len(users):
            room_idx = i // 2
            if room_idx < len(rooms):
                group_id = str(uuid.uuid4())
                assignments.append((rooms[room_idx], users[i], group_id))
                assignments.append((rooms[room_idx], users[i + 1], group_id))
    
    cursor.executemany(
        'INSERT INTO "RoomAssignment" ("roomId", "userId", "groupId") VALUES (%s, %s, %s)',
        assignments
    )
    
    # Update room occupancy
    for room_id in rooms[:len(assignments)//2]:
        cursor.execute('UPDATE "Room" SET occupied = 2 WHERE id = %s', (room_id,))
    
    conn.commit()
    cursor.close()
    print(f"✓ Loaded {len(assignments)} room assignments")


def main():
    """Main function to load all sample data."""
    print("Starting to load sample data...")
    print("-" * 50)
    
    try:
        conn = get_connection()
        print("✓ Connected to database")
        
        # Create tables
        create_tables(conn)
        
        # Load data in order (respecting foreign key constraints)
        load_hostels(conn)
        load_blocks(conn)
        load_floors(conn)
        load_rooms(conn)
        load_users(conn)
        load_friendships(conn)
        load_preferences(conn)
        load_room_assignments(conn)
        
        conn.close()
        
        print("-" * 50)
        print("✓ All sample data loaded successfully!")
        print("\nDefault password for all users: password123")
        
    except Exception as e:
        print(f"✗ Error: {e}")
        raise


if __name__ == "__main__":
    main()

