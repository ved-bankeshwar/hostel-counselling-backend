"""CRUD operations for User model."""

import psycopg2
from psycopg2.extras import RealDictCursor
from typing import Optional, List, Dict, Any

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


def create_user(data: Dict[str, Any]) -> Dict[str, Any]:
    """Create a new user."""
    conn = get_connection()
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(
            """
            INSERT INTO "User" (name, email, "passwordHash", "registrationNumber", gender, rank, hostel, "isActive", role)
            VALUES (%(name)s, %(email)s, %(passwordHash)s, %(registrationNumber)s, %(gender)s, %(rank)s, %(hostel)s, %(isActive)s, %(role)s)
            RETURNING *
            """,
            {
                'name': data['name'],
                'email': data['email'],
                'passwordHash': data['passwordHash'],
                'registrationNumber': data['registrationNumber'],
                'gender': data['gender'],
                'rank': data['rank'],
                'hostel': data['hostel'],
                'isActive': data.get('isActive', True),
                'role': data.get('role', 'user'),
            }
        )
        user = dict(cursor.fetchone())
        conn.commit()
        cursor.close()
        return user
    except Exception as e:
        conn.rollback()
        raise Exception(f"Error creating user: {str(e)}")
    finally:
        conn.close()


def get_user_by_id(user_id: int) -> Optional[Dict[str, Any]]:
    """Get user by ID."""
    conn = get_connection()
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute('SELECT * FROM "User" WHERE id = %s', (user_id,))
        user = cursor.fetchone()
        cursor.close()
        return dict(user) if user else None
    except Exception as e:
        raise Exception(f"Error fetching user: {str(e)}")
    finally:
        conn.close()


def get_all_users(filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    """Get all users with optional filters."""
    conn = get_connection()
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        query = 'SELECT * FROM "User"'
        params = []
        
        if filters:
            conditions = []
            for key, value in filters.items():
                conditions.append(f'"{key}" = %s')
                params.append(value)
            query += ' WHERE ' + ' AND '.join(conditions)
        
        cursor.execute(query, params)
        users = [dict(row) for row in cursor.fetchall()]
        cursor.close()
        return users
    except Exception as e:
        raise Exception(f"Error fetching users: {str(e)}")
    finally:
        conn.close()


def update_user(user_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
    """Update user by ID."""
    conn = get_connection()
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        set_clauses = []
        params = []
        for key, value in data.items():
            set_clauses.append(f'"{key}" = %s')
            params.append(value)
        params.append(user_id)
        
        query = f'UPDATE "User" SET {", ".join(set_clauses)} WHERE id = %s RETURNING *'
        cursor.execute(query, params)
        user = dict(cursor.fetchone())
        conn.commit()
        cursor.close()
        return user
    except Exception as e:
        conn.rollback()
        raise Exception(f"Error updating user: {str(e)}")
    finally:
        conn.close()


def delete_user(user_id: int) -> Dict[str, Any]:
    """Delete user by ID."""
    conn = get_connection()
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute('DELETE FROM "User" WHERE id = %s RETURNING *', (user_id,))
        user = dict(cursor.fetchone())
        conn.commit()
        cursor.close()
        return user
    except Exception as e:
        conn.rollback()
        raise Exception(f"Error deleting user: {str(e)}")
    finally:
        conn.close()


def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    """Get user by email."""
    conn = get_connection()
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute('SELECT * FROM "User" WHERE email = %s', (email,))
        user = cursor.fetchone()
        cursor.close()
        return dict(user) if user else None
    except Exception as e:
        raise Exception(f"Error fetching user by email: {str(e)}")
    finally:
        conn.close()


def get_user_by_registration_number(registration_number: str) -> Optional[Dict[str, Any]]:
    """Get user by registration number."""
    conn = get_connection()
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute('SELECT * FROM "User" WHERE "registrationNumber" = %s', (registration_number,))
        user = cursor.fetchone()
        cursor.close()
        return dict(user) if user else None
    except Exception as e:
        raise Exception(f"Error fetching user by registration number: {str(e)}")
    finally:
        conn.close()


def get_users_by_rank_range(min_rank: int, max_rank: int) -> List[Dict[str, Any]]:
    """Get users within a rank range."""
    conn = get_connection()
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(
            'SELECT * FROM "User" WHERE rank >= %s AND rank <= %s ORDER BY rank ASC',
            (min_rank, max_rank)
        )
        users = [dict(row) for row in cursor.fetchall()]
        cursor.close()
        return users
    except Exception as e:
        raise Exception(f"Error fetching users by rank range: {str(e)}")
    finally:
        conn.close()

