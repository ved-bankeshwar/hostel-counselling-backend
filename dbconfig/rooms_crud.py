import sys
import os
from typing import Optional, Dict, Any

# Add the parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from dbconfig.connection_pool_async import get_connection_pool_async


async def create_room(
    room_number: Optional[str] = None,
    block_name: Optional[str] = None,
    block_letter: Optional[str] = None,
    total_beds: Optional[int] = None,
    floor_id: Optional[int] = None,
) -> Dict[str, Any]:
    """Create a new room in the database."""
    connection_pool = await get_connection_pool_async()
    
    try:
        async with connection_pool.connection() as conn:
            async with conn.cursor() as cur:
                # Prepare the INSERT query
                columns = []
                values = []
                placeholders = []
                
                if room_number is not None:
                    columns.append("room_number")
                    values.append(room_number)
                    placeholders.append("%s")
                
                if block_name is not None:
                    columns.append("block_name")
                    values.append(block_name)
                    placeholders.append("%s")
                
                if block_letter is not None:
                    columns.append("block_letter")
                    values.append(block_letter)
                    placeholders.append("%s")
                
                if total_beds is not None:
                    columns.append("total_beds")
                    values.append(total_beds)
                    placeholders.append("%s")
                
                if floor_id is not None:
                    columns.append("floor_id")
                    values.append(floor_id)
                    placeholders.append("%s")
                
                if not columns:
                    raise ValueError("At least one field must be provided")
                
                query = f"INSERT INTO rooms ({', '.join(columns)}) VALUES ({', '.join(placeholders)}) RETURNING *"
                await cur.execute(query, values)
                result = await cur.fetchone()
                
                if result:
                    # Convert result to dictionary
                    column_names = [desc[0] for desc in cur.description]
                    return dict(zip(column_names, result))
                else:
                    return {"error": "Failed to create room"}
                
    except Exception as e:
        return {"error": str(e)}


async def read_rooms(
    room_number: Optional[str] = None,
    block_name: Optional[str] = None,
    block_letter: Optional[str] = None,
    total_beds: Optional[int] = None,
    floor_id: Optional[int] = None,
    limit: Optional[int] = None,
    offset: Optional[int] = None,
) -> Dict[str, Any]:
    """Read rooms from the database with optional filters."""
    connection_pool = await get_connection_pool_async()
    
    try:
        async with connection_pool.connection() as conn:
            async with conn.cursor() as cur:
                # Build WHERE clause
                where_conditions = []
                values = []
                
                if room_number is not None:
                    where_conditions.append("room_number = %s")
                    values.append(room_number)
                
                if block_name is not None:
                    where_conditions.append("block_name ILIKE %s")
                    values.append(f"%{block_name}%")
                
                if block_letter is not None:
                    where_conditions.append("block_letter = %s")
                    values.append(block_letter)
                
                if total_beds is not None:
                    where_conditions.append("total_beds = %s")
                    values.append(total_beds)
                
                if floor_id is not None:
                    where_conditions.append("floor_id = %s")
                    values.append(floor_id)
                
                # Build the query
                query = "SELECT * FROM rooms"
                if where_conditions:
                    query += " WHERE " + " AND ".join(where_conditions)
                
                query += " ORDER BY block_letter, room_number"
                
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


async def update_room(
    room_number: str,
    block_name: Optional[str] = None,
    block_letter: Optional[str] = None,
    total_beds: Optional[int] = None,
    floor_id: Optional[int] = None,
) -> Dict[str, Any]:
    """Update a room in the database using room_number as identifier."""
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
                
                if block_letter is not None:
                    set_clauses.append("block_letter = %s")
                    values.append(block_letter)
                
                if total_beds is not None:
                    set_clauses.append("total_beds = %s")
                    values.append(total_beds)
                
                if floor_id is not None:
                    set_clauses.append("floor_id = %s")
                    values.append(floor_id)
                
                if not set_clauses:
                    raise ValueError("At least one field must be provided for update")
                
                # Add room_number to values
                values.append(room_number)
                
                query = f"UPDATE rooms SET {', '.join(set_clauses)} WHERE room_number = %s RETURNING *"
                await cur.execute(query, values)
                result = await cur.fetchone()
                
                if result:
                    column_names = [desc[0] for desc in cur.description]
                    return dict(zip(column_names, result))
                else:
                    return {"error": "Room not found or update failed"}
                
    except Exception as e:
        return {"error": str(e)}


async def delete_room(
    room_number: str
) -> Dict[str, Any]:
    """Delete a room from the database using room_number."""
    connection_pool = await get_connection_pool_async()
    
    try:
        async with connection_pool.connection() as conn:
            async with conn.cursor() as cur:
                query = "DELETE FROM rooms WHERE room_number = %s RETURNING *"
                await cur.execute(query, [room_number])
                result = await cur.fetchone()
                
                if result:
                    column_names = [desc[0] for desc in cur.description]
                    return {
                        "deleted": True,
                        "data": dict(zip(column_names, result))
                    }
                else:
                    return {"error": "Room not found"}
                
    except Exception as e:
        return {"error": str(e)}
