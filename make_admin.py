"""Make a user an admin by email or ID."""
import psycopg2
from psycopg2.extras import RealDictCursor
import sys
from config import DB_CONFIG

def make_admin(identifier: str, by_email: bool = True):
    """Make a user admin by email or ID."""
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        if by_email:
            cursor.execute('SELECT * FROM "User" WHERE email = %s', (identifier,))
        else:
            cursor.execute('SELECT * FROM "User" WHERE id = %s', (int(identifier),))
        
        user = cursor.fetchone()
        
        if not user:
            print(f"❌ User not found: {identifier}")
            return False
        
        # Update to admin
        cursor.execute(
            'UPDATE "User" SET role = %s WHERE id = %s RETURNING *',
            ('admin', user['id'])
        )
        
        updated_user = cursor.fetchone()
        conn.commit()
        
        print(f"✅ User promoted to admin!")
        print(f"   ID: {updated_user['id']}")
        print(f"   Email: {updated_user['email']}")
        print(f"   Display Name: {updated_user.get('displayName', 'N/A')}")
        print(f"   Role: {updated_user['role']}")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Error: {str(e)}")
        cursor.close()
        conn.close()
        return False


def list_users():
    """List all users with their roles."""
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        cursor.execute('SELECT id, email, "displayName", role FROM "User" ORDER BY id')
        users = cursor.fetchall()
        
        if not users:
            print("📋 No users found in database")
            return
        
        print(f"\n📋 Total Users: {len(users)}\n")
        print(f"{'ID':<5} {'Email':<35} {'Display Name':<25} {'Role':<10}")
        print("=" * 80)
        
        for user in users:
            display_name = user.get('displayName', 'N/A') or 'N/A'
            role = user['role'] or 'user'
            print(f"{user['id']:<5} {user['email']:<35} {display_name:<25} {role:<10}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        cursor.close()
        conn.close()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("🔐 Make User Admin Tool\n")
        print("Usage:")
        print("  python make_admin.py <email>           - Make user admin by email")
        print("  python make_admin.py --id <user_id>    - Make user admin by ID")
        print("  python make_admin.py --list            - List all users")
        print("\nExamples:")
        print("  python make_admin.py user@example.com")
        print("  python make_admin.py --id 1")
        print("  python make_admin.py --list")
        sys.exit(1)
    
    if sys.argv[1] == "--list":
        list_users()
    elif sys.argv[1] == "--id":
        if len(sys.argv) < 3:
            print("❌ Please provide user ID")
            sys.exit(1)
        make_admin(sys.argv[2], by_email=False)
    else:
        make_admin(sys.argv[1], by_email=True)
