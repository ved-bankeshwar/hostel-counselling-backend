import sys
import os
from typing import Optional, Dict, Any

# Add the parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from dbconfig.connection_pool_async import get_connection_pool_async


async def create_friend(
    user_id: Optional[str] = None,
    friend_id: Optional[str] = None,
) -> Dict[str, Any]:
    """Create a new friend relationship in the database."""
    connection_pool = await get_connection_pool_async()
    
    try:
        async with connection_pool.connection() as conn:
            async with conn.cursor() as cur:
                # Prepare the INSERT query
                columns = []
                values = []
                placeholders = []
                
                if user_id is not None:
                    columns.append("user_id")
                    values.append(user_id)
                    placeholders.append("%s")
                
                if friend_id is not None:
                    columns.append("friend_id")
                    values.append(friend_id)
                    placeholders.append("%s")
                
                if not columns:
                    raise ValueError("At least one field must be provided")
                
                query = f"INSERT INTO friends ({', '.join(columns)}) VALUES ({', '.join(placeholders)}) RETURNING *"
                await cur.execute(query, values)
                result = await cur.fetchone()
                
                if result:
                    # Convert result to dictionary
                    column_names = [desc[0] for desc in cur.description]
                    return dict(zip(column_names, result))
                else:
                    return {"error": "Failed to create friend relationship"}
                
    except Exception as e:
        return {"error": str(e)}


async def read_friends(
    user_id: Optional[str] = None,
    friend_id: Optional[str] = None,
    limit: Optional[int] = None,
    offset: Optional[int] = None,
) -> Dict[str, Any]:
    """Read friend relationships from the database with optional filters."""
    connection_pool = await get_connection_pool_async()
    
    try:
        async with connection_pool.connection() as conn:
            async with conn.cursor() as cur:
                # Build WHERE clause
                where_conditions = []
                values = []
                
                if user_id is not None:
                    where_conditions.append("user_id = %s")
                    values.append(user_id)
                
                if friend_id is not None:
                    where_conditions.append("friend_id = %s")
                    values.append(friend_id)
                
                # Build the query
                query = "SELECT * FROM friends"
                if where_conditions:
                    query += " WHERE " + " AND ".join(where_conditions)
                
                query += " ORDER BY user_id, friend_id"
                
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


async def update_friend(
    user_id: str,
    friend_id: str,
    new_user_id: Optional[str] = None,
    new_friend_id: Optional[str] = None,
) -> Dict[str, Any]:
    """Update a friend relationship in the database using user_id and friend_id as identifiers."""
    connection_pool = await get_connection_pool_async()
    
    try:
        async with connection_pool.connection() as conn:
            async with conn.cursor() as cur:
                # Build SET clause for fields that are provided
                set_clauses = []
                values = []
                
                if new_user_id is not None:
                    set_clauses.append("user_id = %s")
                    values.append(new_user_id)
                
                if new_friend_id is not None:
                    set_clauses.append("friend_id = %s")
                    values.append(new_friend_id)
                
                if not set_clauses:
                    raise ValueError("At least one field must be provided for update")
                
                # Add user_id and friend_id to values
                values.extend([user_id, friend_id])
                
                query = f"UPDATE friends SET {', '.join(set_clauses)} WHERE user_id = %s AND friend_id = %s RETURNING *"
                await cur.execute(query, values)
                result = await cur.fetchone()
                
                if result:
                    column_names = [desc[0] for desc in cur.description]
                    return dict(zip(column_names, result))
                else:
                    return {"error": "Friend relationship not found or update failed"}
                
    except Exception as e:
        return {"error": str(e)}


async def delete_friend(
    user_id: str,
    friend_id: str
) -> Dict[str, Any]:
    """Delete a friend relationship from the database using user_id and friend_id."""
    connection_pool = await get_connection_pool_async()
    
    try:
        async with connection_pool.connection() as conn:
            async with conn.cursor() as cur:
                query = "DELETE FROM friends WHERE user_id = %s AND friend_id = %s RETURNING *"
                await cur.execute(query, [user_id, friend_id])
                result = await cur.fetchone()
                
                if result:
                    column_names = [desc[0] for desc in cur.description]
                    return {
                        "deleted": True,
                        "data": dict(zip(column_names, result))
                    }
                else:
                    return {"error": "Friend relationship not found"}
                
    except Exception as e:
        return {"error": str(e)}


