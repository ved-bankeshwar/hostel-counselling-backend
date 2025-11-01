"""CRUD operations for RoomAssignment model."""

import psycopg2
from psycopg2.extras import RealDictCursor
from typing import Optional, List, Dict, Any
import uuid

# Database connection parameters
DB_CONFIG = {
    'host': 'localhost',
    'port': 5433,
    'database': 'room_counselling',
    'user': 'admin',
    'password': 'admin'
}


def get_connection():
    """Create and return a database connection."""
    return psycopg2.connect(**DB_CONFIG)


def create_room_assignment(data: Dict[str, Any]) -> Dict[str, Any]:
    """Create a new room assignment."""
    conn = get_connection()
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        group_id = data.get('groupId', str(uuid.uuid4()))
        
        cursor.execute(
            """
            INSERT INTO "RoomAssignment" ("roomId", "userId", "groupId")
            VALUES (%(roomId)s, %(userId)s, %(groupId)s)
            RETURNING *
            """,
            {
                'roomId': data['roomId'],
                'userId': data['userId'],
                'groupId': group_id,
            }
        )
        room_assignment = dict(cursor.fetchone())
        conn.commit()
        cursor.close()
        return room_assignment
    except Exception as e:
        conn.rollback()
        raise Exception(f"Error creating room assignment: {str(e)}")
    finally:
        conn.close()


def get_room_assignment_by_id(assignment_id: int) -> Optional[Dict[str, Any]]:
    """Get room assignment by ID."""
    conn = get_connection()
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute('SELECT * FROM "RoomAssignment" WHERE id = %s', (assignment_id,))
        room_assignment = cursor.fetchone()
        cursor.close()
        return dict(room_assignment) if room_assignment else None
    except Exception as e:
        raise Exception(f"Error fetching room assignment: {str(e)}")
    finally:
        conn.close()


def get_all_room_assignments(filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    """Get all room assignments with optional filters."""
    conn = get_connection()
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        query = 'SELECT * FROM "RoomAssignment"'
        params = []
        
        if filters:
            conditions = []
            for key, value in filters.items():
                conditions.append(f'"{key}" = %s')
                params.append(value)
            query += ' WHERE ' + ' AND '.join(conditions)
        
        cursor.execute(query, params)
        room_assignments = [dict(row) for row in cursor.fetchall()]
        cursor.close()
        return room_assignments
    except Exception as e:
        raise Exception(f"Error fetching room assignments: {str(e)}")
    finally:
        conn.close()


def update_room_assignment(assignment_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
    """Update room assignment by ID."""
    conn = get_connection()
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        set_clauses = []
        params = []
        for key, value in data.items():
            set_clauses.append(f'"{key}" = %s')
            params.append(value)
        params.append(assignment_id)
        
        query = f'UPDATE "RoomAssignment" SET {", ".join(set_clauses)} WHERE id = %s RETURNING *'
        cursor.execute(query, params)
        room_assignment = dict(cursor.fetchone())
        conn.commit()
        cursor.close()
        return room_assignment
    except Exception as e:
        conn.rollback()
        raise Exception(f"Error updating room assignment: {str(e)}")
    finally:
        conn.close()


def delete_room_assignment(assignment_id: int) -> Dict[str, Any]:
    """Delete room assignment by ID."""
    conn = get_connection()
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute('DELETE FROM "RoomAssignment" WHERE id = %s RETURNING *', (assignment_id,))
        room_assignment = dict(cursor.fetchone())
        conn.commit()
        cursor.close()
        return room_assignment
    except Exception as e:
        conn.rollback()
        raise Exception(f"Error deleting room assignment: {str(e)}")
    finally:
        conn.close()


def get_room_assignments_by_user_id(user_id: int) -> List[Dict[str, Any]]:
    """Get all room assignments for a specific user."""
    conn = get_connection()
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute('SELECT * FROM "RoomAssignment" WHERE "userId" = %s', (user_id,))
        room_assignments = [dict(row) for row in cursor.fetchall()]
        cursor.close()
        return room_assignments
    except Exception as e:
        raise Exception(f"Error fetching room assignments by user ID: {str(e)}")
    finally:
        conn.close()


def get_room_assignments_by_room_id(room_id: int) -> List[Dict[str, Any]]:
    """Get all room assignments for a specific room."""
    conn = get_connection()
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute('SELECT * FROM "RoomAssignment" WHERE "roomId" = %s', (room_id,))
        room_assignments = [dict(row) for row in cursor.fetchall()]
        cursor.close()
        return room_assignments
    except Exception as e:
        raise Exception(f"Error fetching room assignments by room ID: {str(e)}")
    finally:
        conn.close()


def get_room_assignments_by_group_id(group_id: str) -> List[Dict[str, Any]]:
    """Get all room assignments for a specific group."""
    conn = get_connection()
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute('SELECT * FROM "RoomAssignment" WHERE "groupId" = %s', (group_id,))
        room_assignments = [dict(row) for row in cursor.fetchall()]
        cursor.close()
        return room_assignments
    except Exception as e:
        raise Exception(f"Error fetching room assignments by group ID: {str(e)}")
    finally:
        conn.close()


def delete_room_assignments_by_user_id(user_id: int) -> int:
    """Delete all room assignments for a specific user."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM "RoomAssignment" WHERE "userId" = %s', (user_id,))
        count = cursor.rowcount
        conn.commit()
        cursor.close()
        return count
    except Exception as e:
        conn.rollback()
        raise Exception(f"Error deleting room assignments by user ID: {str(e)}")
    finally:
        conn.close()


def bulk_create_room_assignments(assignments_data: List[Dict[str, Any]]) -> int:
    """Bulk create multiple room assignments."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        count = 0
        for assignment_data in assignments_data:
            group_id = assignment_data.get('groupId', str(uuid.uuid4()))
            cursor.execute(
                """
                INSERT INTO "RoomAssignment" ("roomId", "userId", "groupId")
                VALUES (%(roomId)s, %(userId)s, %(groupId)s)
                """,
                {
                    'roomId': assignment_data['roomId'],
                    'userId': assignment_data['userId'],
                    'groupId': group_id,
                }
            )
            count += 1
        conn.commit()
        cursor.close()
        return count
    except Exception as e:
        conn.rollback()
        raise Exception(f"Error bulk creating room assignments: {str(e)}")
    finally:
        conn.close()

