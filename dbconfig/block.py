"""CRUD operations for Block model."""

import psycopg2
from psycopg2.extras import RealDictCursor
from typing import Optional, List, Dict, Any

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


def create_block(data: Dict[str, Any]) -> Dict[str, Any]:
    """Create a new block."""
    conn = get_connection()
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(
            """
            INSERT INTO "Block" ("hostelId", "blockName", "isAC", "isDeluxe", "isApartment")
            VALUES (%(hostelId)s, %(blockName)s, %(isAC)s, %(isDeluxe)s, %(isApartment)s)
            RETURNING *
            """,
            {
                'hostelId': data['hostelId'],
                'blockName': data['blockName'],
                'isAC': data['isAC'],
                'isDeluxe': data['isDeluxe'],
                'isApartment': data['isApartment'],
            }
        )
        block = dict(cursor.fetchone())
        conn.commit()
        cursor.close()
        return block
    except Exception as e:
        conn.rollback()
        raise Exception(f"Error creating block: {str(e)}")
    finally:
        conn.close()


def get_block_by_id(block_id: int) -> Optional[Dict[str, Any]]:
    """Get block by ID."""
    conn = get_connection()
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute('SELECT * FROM "Block" WHERE id = %s', (block_id,))
        block = cursor.fetchone()
        cursor.close()
        return dict(block) if block else None
    except Exception as e:
        raise Exception(f"Error fetching block: {str(e)}")
    finally:
        conn.close()


def get_all_blocks(filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    """Get all blocks with optional filters."""
    conn = get_connection()
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        query = 'SELECT * FROM "Block"'
        params = []
        
        if filters:
            conditions = []
            for key, value in filters.items():
                conditions.append(f'"{key}" = %s')
                params.append(value)
            query += ' WHERE ' + ' AND '.join(conditions)
        
        cursor.execute(query, params)
        blocks = [dict(row) for row in cursor.fetchall()]
        cursor.close()
        return blocks
    except Exception as e:
        raise Exception(f"Error fetching blocks: {str(e)}")
    finally:
        conn.close()


def update_block(block_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
    """Update block by ID."""
    conn = get_connection()
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        set_clauses = []
        params = []
        for key, value in data.items():
            set_clauses.append(f'"{key}" = %s')
            params.append(value)
        params.append(block_id)
        
        query = f'UPDATE "Block" SET {", ".join(set_clauses)} WHERE id = %s RETURNING *'
        cursor.execute(query, params)
        block = dict(cursor.fetchone())
        conn.commit()
        cursor.close()
        return block
    except Exception as e:
        conn.rollback()
        raise Exception(f"Error updating block: {str(e)}")
    finally:
        conn.close()


def delete_block(block_id: int) -> Dict[str, Any]:
    """Delete block by ID."""
    conn = get_connection()
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute('DELETE FROM "Block" WHERE id = %s RETURNING *', (block_id,))
        block = dict(cursor.fetchone())
        conn.commit()
        cursor.close()
        return block
    except Exception as e:
        conn.rollback()
        raise Exception(f"Error deleting block: {str(e)}")
    finally:
        conn.close()


def get_blocks_by_hostel_id(hostel_id: int) -> List[Dict[str, Any]]:
    """Get all blocks for a specific hostel."""
    conn = get_connection()
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute('SELECT * FROM "Block" WHERE "hostelId" = %s', (hostel_id,))
        blocks = [dict(row) for row in cursor.fetchall()]
        cursor.close()
        return blocks
    except Exception as e:
        raise Exception(f"Error fetching blocks by hostel ID: {str(e)}")
    finally:
        conn.close()


def get_ac_blocks() -> List[Dict[str, Any]]:
    """Get all AC blocks."""
    conn = get_connection()
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute('SELECT * FROM "Block" WHERE "isAC" = true')
        blocks = [dict(row) for row in cursor.fetchall()]
        cursor.close()
        return blocks
    except Exception as e:
        raise Exception(f"Error fetching AC blocks: {str(e)}")
    finally:
        conn.close()
