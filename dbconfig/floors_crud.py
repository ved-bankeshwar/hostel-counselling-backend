import sys
import os
from typing import Optional, Dict, Any

# Add the parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from dbconfig.connection_pool_async import get_connection_pool_async


async def create_floor(
    floor_id: Optional[int] = None,
    floor_number: Optional[int] = None,
    block_letter: Optional[str] = None,
) -> Dict[str, Any]:
    """Create a new floor in the database."""
    connection_pool = await get_connection_pool_async()
    
    try:
        async with connection_pool.connection() as conn:
            async with conn.cursor() as cur:
                # Prepare the INSERT query
                columns = []
                values = []
                placeholders = []
                
                if floor_id is not None:
                    columns.append("floor_id")
                    values.append(floor_id)
                    placeholders.append("%s")
                
                if floor_number is not None:
                    columns.append("floor_number")
                    values.append(floor_number)
                    placeholders.append("%s")
                
                if block_letter is not None:
                    columns.append("block_letter")
                    values.append(block_letter)
                    placeholders.append("%s")
                
                if not columns:
                    raise ValueError("At least one field must be provided")
                
                query = f"INSERT INTO floors ({', '.join(columns)}) VALUES ({', '.join(placeholders)}) RETURNING *"
                await cur.execute(query, values)
                result = await cur.fetchone()
                
                if result:
                    # Convert result to dictionary
                    column_names = [desc[0] for desc in cur.description]
                    return dict(zip(column_names, result))
                else:
                    return {"error": "Failed to create floor"}
                
    except Exception as e:
        return {"error": str(e)}


async def read_floors(
    floor_id: Optional[int] = None,
    floor_number: Optional[int] = None,
    block_letter: Optional[str] = None,
    limit: Optional[int] = None,
    offset: Optional[int] = None,
) -> Dict[str, Any]:
    """Read floors from the database with optional filters."""
    connection_pool = await get_connection_pool_async()
    
    try:
        async with connection_pool.connection() as conn:
            async with conn.cursor() as cur:
                # Build WHERE clause
                where_conditions = []
                values = []
                
                if floor_id is not None:
                    where_conditions.append("floor_id = %s")
                    values.append(floor_id)
                
                if floor_number is not None:
                    where_conditions.append("floor_number = %s")
                    values.append(floor_number)
                
                if block_letter is not None:
                    where_conditions.append("block_letter = %s")
                    values.append(block_letter)
                
                # Build the query
                query = "SELECT * FROM floors"
                if where_conditions:
                    query += " WHERE " + " AND ".join(where_conditions)
                
                query += " ORDER BY block_letter, floor_number"
                
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


async def update_floor(
    floor_id: int,
    floor_number: Optional[int] = None,
    block_letter: Optional[str] = None,
) -> Dict[str, Any]:
    """Update a floor in the database using floor_id as identifier."""
    connection_pool = await get_connection_pool_async()
    
    try:
        async with connection_pool.connection() as conn:
            async with conn.cursor() as cur:
                # Build SET clause for fields that are provided
                set_clauses = []
                values = []
                
                if floor_number is not None:
                    set_clauses.append("floor_number = %s")
                    values.append(floor_number)
                
                if block_letter is not None:
                    set_clauses.append("block_letter = %s")
                    values.append(block_letter)
                
                if not set_clauses:
                    raise ValueError("At least one field must be provided for update")
                
                # Add floor_id to values
                values.append(floor_id)
                
                query = f"UPDATE floors SET {', '.join(set_clauses)} WHERE floor_id = %s RETURNING *"
                await cur.execute(query, values)
                result = await cur.fetchone()
                
                if result:
                    column_names = [desc[0] for desc in cur.description]
                    return dict(zip(column_names, result))
                else:
                    return {"error": "Floor not found or update failed"}
                
    except Exception as e:
        return {"error": str(e)}


async def delete_floor(
    floor_id: int
) -> Dict[str, Any]:
    """Delete a floor from the database using floor_id."""
    connection_pool = await get_connection_pool_async()
    
    try:
        async with connection_pool.connection() as conn:
            async with conn.cursor() as cur:
                query = "DELETE FROM floors WHERE floor_id = %s RETURNING *"
                await cur.execute(query, [floor_id])
                result = await cur.fetchone()
                
                if result:
                    column_names = [desc[0] for desc in cur.description]
                    return {
                        "deleted": True,
                        "data": dict(zip(column_names, result))
                    }
                else:
                    return {"error": "Floor not found"}
                
    except Exception as e:
        return {"error": str(e)}
