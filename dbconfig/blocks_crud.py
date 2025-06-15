import sys
import os
from typing import Optional, Dict, Any

# Add the parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from dbconfig.connection_pool_async import get_connection_pool_async


async def create_block(
    block_letter: Optional[str] = None,
    block_name: Optional[str] = None,
    is_deluxe: Optional[bool] = None,
    is_ac: Optional[bool] = None,
) -> Dict[str, Any]:
    """Create a new block in the database."""
    connection_pool = await get_connection_pool_async()
    
    try:
        async with connection_pool.connection() as conn:
            async with conn.cursor() as cur:
                # Prepare the INSERT query
                columns = []
                values = []
                placeholders = []
                
                if block_letter is not None:
                    columns.append("block_letter")
                    values.append(block_letter)
                    placeholders.append("%s")
                
                if block_name is not None:
                    columns.append("block_name")
                    values.append(block_name)
                    placeholders.append("%s")
                
                if is_deluxe is not None:
                    columns.append("is_deluxe")
                    values.append(is_deluxe)
                    placeholders.append("%s")
                
                if is_ac is not None:
                    columns.append("is_ac")
                    values.append(is_ac)
                    placeholders.append("%s")
                
                if not columns:
                    raise ValueError("At least one field must be provided")
                
                query = f"INSERT INTO blocks ({', '.join(columns)}) VALUES ({', '.join(placeholders)}) RETURNING *"
                await cur.execute(query, values)
                result = await cur.fetchone()
                
                if result:
                    # Convert result to dictionary
                    column_names = [desc[0] for desc in cur.description]
                    return dict(zip(column_names, result))
                else:
                    return {"error": "Failed to create block"}
                
    except Exception as e:
        return {"error": str(e)}


async def read_blocks(
    block_letter: Optional[str] = None,
    block_name: Optional[str] = None,
    is_deluxe: Optional[bool] = None,
    is_ac: Optional[bool] = None,
    limit: Optional[int] = None,
    offset: Optional[int] = None,
) -> Dict[str, Any]:
    """Read blocks from the database with optional filters."""
    connection_pool = await get_connection_pool_async()
    
    try:
        async with connection_pool.connection() as conn:
            async with conn.cursor() as cur:
                # Build WHERE clause
                where_conditions = []
                values = []
                
                if block_letter is not None:
                    where_conditions.append("block_letter = %s")
                    values.append(block_letter)
                
                if block_name is not None:
                    where_conditions.append("block_name ILIKE %s")
                    values.append(f"%{block_name}%")
                
                if is_deluxe is not None:
                    where_conditions.append("is_deluxe = %s")
                    values.append(is_deluxe)
                
                if is_ac is not None:
                    where_conditions.append("is_ac = %s")
                    values.append(is_ac)
                
                # Build the query
                query = "SELECT * FROM blocks"
                if where_conditions:
                    query += " WHERE " + " AND ".join(where_conditions)
                
                query += " ORDER BY block_letter"
                
                if limit is not None:
                    query += f" LIMIT {limit}"
                
                if offset is not None:
                    query += f" OFFSET {offset}"
                
                await cur.execute(query, values)
                results = await cur.fetchall()
                
                if results:
                    column_names = [desc[0] for desc in cur.description]
                    return {
                        "data": [dict(zip(column_names, row)) for row in results],
                        "count": len(results)
                    }
                else:
                    return {"data": [], "count": 0}
                
    except Exception as e:
        return {"error": str(e)}


async def update_block(
    block_letter: str,
    block_name: Optional[str] = None,
    is_deluxe: Optional[bool] = None,
    is_ac: Optional[bool] = None,
) -> Dict[str, Any]:
    """Update a block in the database using block_letter as identifier."""
    connection_pool = await get_connection_pool_async()
    
    try:
        async with connection_pool.connection() as conn:
            async with conn.cursor() as cur:
                # Build SET clause for fields that are provided
                set_clauses = []
                values = []
                
                if block_name is not None:
                    set_clauses.append("block_name = %s")
                    values.append(block_name)
                
                if is_deluxe is not None:
                    set_clauses.append("is_deluxe = %s")
                    values.append(is_deluxe)
                
                if is_ac is not None:
                    set_clauses.append("is_ac = %s")
                    values.append(is_ac)
                
                if not set_clauses:
                    raise ValueError("At least one field must be provided for update")
                
                # Add block_letter to values
                values.append(block_letter)
                
                query = f"UPDATE blocks SET {', '.join(set_clauses)} WHERE block_letter = %s RETURNING *"
                await cur.execute(query, values)
                result = await cur.fetchone()
                
                if result:
                    column_names = [desc[0] for desc in cur.description]
                    return dict(zip(column_names, result))
                else:
                    return {"error": "Block not found or update failed"}
                
    except Exception as e:
        return {"error": str(e)}


async def delete_block(
    block_letter: str
) -> Dict[str, Any]:
    """Delete a block from the database using block_letter."""
    connection_pool = await get_connection_pool_async()
    
    try:
        async with connection_pool.connection() as conn:
            async with conn.cursor() as cur:
                query = "DELETE FROM blocks WHERE block_letter = %s RETURNING *"
                await cur.execute(query, [block_letter])
                result = await cur.fetchone()
                
                if result:
                    column_names = [desc[0] for desc in cur.description]
                    return {
                        "deleted": True,
                        "data": dict(zip(column_names, result))
                    }
                else:
                    return {"error": "Block not found"}
                
    except Exception as e:
        return {"error": str(e)}
