"""Run the denormalization migration"""
import psycopg2
from psycopg2.extras import RealDictCursor

DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'room_counselling',
    'user': 'admin',
    'password': 'admin123'
}

def run_migration():
    """Execute the denormalization migration"""
    print("Starting denormalization migration...")
    print("=" * 80)
    
    # Read migration file
    with open('migrations/005_denormalize_to_rooms_table.sql', 'r') as f:
        migration_sql = f.read()
    
    conn = psycopg2.connect(**DB_CONFIG)
    
    try:
        cursor = conn.cursor()
        
        # Execute migration
        print("\nExecuting migration SQL...")
        cursor.execute(migration_sql)
        
        conn.commit()
        print("\n✓ Migration completed successfully!")
        
        # Verify the new table
        cursor.execute('SELECT COUNT(*) FROM "Rooms"')
        rooms_count = cursor.fetchone()[0]
        print(f"\n✓ New Rooms table created with {rooms_count} rooms")
        
        # Check a sample room
        cursor.execute('SELECT * FROM "Rooms" LIMIT 1')
        sample = cursor.fetchone()
        if sample:
            print(f"\nSample room data:")
            print(f"  Room Number: {sample[1]}")
            print(f"  Floor: {sample[2]}")
            print(f"  Block: {sample[3]} ({sample[4]})")
            print(f"  Hostel: {sample[5]} ({sample[6]})")
            print(f"  Capacity: {sample[8]}")
            print(f"  Occupied: {sample[9]}")
        
        cursor.close()
        
    except Exception as e:
        conn.rollback()
        print(f"\n✗ Migration failed: {str(e)}")
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    run_migration()
