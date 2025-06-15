import sys
import os
from typing import Optional, Dict, Any

# Add the parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from dbconfig.connection_pool_async import get_connection_pool_async


async def create_allotment(
    allotment_id: Optional[int] = None,
    user_id: Optional[str] = None,
    block_letter: Optional[str] = None,
    room_number: Optional[str] = None,
    allotment_date: Optional[int] = None,
    is_alloted: Optional[bool] = None,
) -> Dict[str, Any]:
    """Create a new allotment in the database."""
    connection_pool = await get_connection_pool_async()
    
    try:
        async with connection_pool.connection() as conn:
            async with conn.cursor() as cur:
                # Prepare the INSERT query
                columns = []
                values = []
                placeholders = []
                
                if allotment_id is not None:
                    columns.append("allotment_id")
                    values.append(allotment_id)
                    placeholders.append("%s")
                
                if user_id is not None:
                    columns.append("user_id")
                    values.append(user_id)
                    placeholders.append("%s")
                
                if block_letter is not None:
                    columns.append("block_letter")
                    values.append(block_letter)
                    placeholders.append("%s")
                
                if room_number is not None:
                    columns.append("room_number")
                    values.append(room_number)
                    placeholders.append("%s")
                
                if allotment_date is not None:
                    columns.append("allotment_date")
                    values.append(allotment_date)
                    placeholders.append("%s")
                
                if is_alloted is not None:
                    columns.append("is_alloted")
                    values.append(is_alloted)
                    placeholders.append("%s")
                
                if not columns:
                    raise ValueError("At least one field must be provided")
                
                query = f"INSERT INTO allotments ({', '.join(columns)}) VALUES ({', '.join(placeholders)}) RETURNING *"
                await cur.execute(query, values)
                result = await cur.fetchone()
                
                if result:
                    # Convert result to dictionary
                    column_names = [desc[0] for desc in cur.description]
                    return dict(zip(column_names, result))
                else:
                    return {"error": "Failed to create allotment"}
                
    except Exception as e:
        return {"error": str(e)}


async def read_allotments(
    allotment_id: Optional[int] = None,
    user_id: Optional[str] = None,
    block_letter: Optional[str] = None,
    room_number: Optional[str] = None,
    allotment_date: Optional[int] = None,
    is_alloted: Optional[bool] = None,
    limit: Optional[int] = None,
    offset: Optional[int] = None,
) -> Dict[str, Any]:
    """Read allotments from the database with optional filters."""
    connection_pool = await get_connection_pool_async()
    
    try:
        async with connection_pool.connection() as conn:
            async with conn.cursor() as cur:
                # Build WHERE clause
                where_conditions = []
                values = []
                
                if allotment_id is not None:
                    where_conditions.append("allotment_id = %s")
                    values.append(allotment_id)
                
                if user_id is not None:
                    where_conditions.append("user_id = %s")
                    values.append(user_id)
                
                if block_letter is not None:
                    where_conditions.append("block_letter = %s")
                    values.append(block_letter)
                
                if room_number is not None:
                    where_conditions.append("room_number = %s")
                    values.append(room_number)
                
                if allotment_date is not None:
                    where_conditions.append("allotment_date = %s")
                    values.append(allotment_date)
                
                if is_alloted is not None:
                    where_conditions.append("is_alloted = %s")
                    values.append(is_alloted)
                
                # Build the query
                query = "SELECT * FROM allotments"
                if where_conditions:
                    query += " WHERE " + " AND ".join(where_conditions)
                
                query += " ORDER BY allotment_date DESC"
                
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


async def update_allotment(
    allotment_id: int,
    user_id: Optional[str] = None,
    block_letter: Optional[str] = None,
    room_number: Optional[str] = None,
    allotment_date: Optional[int] = None,
    is_alloted: Optional[bool] = None,
) -> Dict[str, Any]:
    """Update an allotment in the database using allotment_id as identifier."""
    connection_pool = await get_connection_pool_async()
    
    try:
        async with connection_pool.connection() as conn:
            async with conn.cursor() as cur:
                # Build SET clause for fields that are provided
                set_clauses = []
                values = []
                
                if user_id is not None:
                    set_clauses.append("user_id = %s")
                    values.append(user_id)
                
                if block_letter is not None:
                    set_clauses.append("block_letter = %s")
                    values.append(block_letter)
                
                if room_number is not None:
                    set_clauses.append("room_number = %s")
                    values.append(room_number)
                
                if allotment_date is not None:
                    set_clauses.append("allotment_date = %s")
                    values.append(allotment_date)
                
                if is_alloted is not None:
                    set_clauses.append("is_alloted = %s")
                    values.append(is_alloted)
                
                if not set_clauses:
                    raise ValueError("At least one field must be provided for update")
                
                # Add allotment_id to values
                values.append(allotment_id)
                
                query = f"UPDATE allotments SET {', '.join(set_clauses)} WHERE allotment_id = %s RETURNING *"
                await cur.execute(query, values)
                result = await cur.fetchone()
                
                if result:
                    column_names = [desc[0] for desc in cur.description]
                    return dict(zip(column_names, result))
                else:
                    return {"error": "Allotment not found or update failed"}
                
    except Exception as e:
        return {"error": str(e)}


async def delete_allotment(
    allotment_id: int
) -> Dict[str, Any]:
    """Delete an allotment from the database using allotment_id."""
    connection_pool = await get_connection_pool_async()
    
    try:
        async with connection_pool.connection() as conn:
            async with conn.cursor() as cur:
                query = "DELETE FROM allotments WHERE allotment_id = %s RETURNING *"
                await cur.execute(query, [allotment_id])
                result = await cur.fetchone()
                
                if result:
                    column_names = [desc[0] for desc in cur.description]
                    return {
                        "deleted": True,
                        "data": dict(zip(column_names, result))
                    }
                else:
                    return {"error": "Allotment not found"}
                
    except Exception as e:
        return {"error": str(e)}
