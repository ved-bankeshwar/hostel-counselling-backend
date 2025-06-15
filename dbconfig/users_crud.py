import sys
import os
from typing import Optional, Dict, List, Any

# Add the parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from dbconfig.connection_pool_async import get_connection_pool_async


async def create_user(
    user_id: Optional[str] = None,
    email: Optional[str] = None,
    registration_number: Optional[str] = None,
    name: Optional[str] = None,
    group: Optional[int] = None,
    course: Optional[str] = None,
    year_of_study: Optional[int] = None,
    time_to_allotment: Optional[int] = None,
    is_alloted: Optional[bool] = None,
    mobile_number: Optional[str] = None,
    role: Optional[str] = None,
    privilages: Optional[List[str]] = None,
    rank: Optional[int] = None,
    created_at: Optional[int] = None,
    updated_at: Optional[int] = None,
) -> Dict[str, Any]:
    """Create a new user in the database."""
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
                
                if email is not None:
                    columns.append("email")
                    values.append(email)
                    placeholders.append("%s")
                
                if registration_number is not None:
                    columns.append("registration_number")
                    values.append(registration_number)
                    placeholders.append("%s")
                
                if name is not None:
                    columns.append("name")
                    values.append(name)
                    placeholders.append("%s")
                
                if group is not None:
                    columns.append("group")
                    values.append(group)
                    placeholders.append("%s")
                
                if course is not None:
                    columns.append("course")
                    values.append(course)
                    placeholders.append("%s")
                
                if year_of_study is not None:
                    columns.append("year_of_study")
                    values.append(year_of_study)
                    placeholders.append("%s")
                
                if time_to_allotment is not None:
                    columns.append("time_to_allotment")
                    values.append(time_to_allotment)
                    placeholders.append("%s")
                
                if is_alloted is not None:
                    columns.append("is_alloted")
                    values.append(is_alloted)
                    placeholders.append("%s")
                if mobile_number is not None:
                    columns.append("mobile_number")
                    values.append(mobile_number)
                    placeholders.append("%s")
                
                if role is not None:
                    columns.append("role")
                    values.append(role)
                    placeholders.append("%s")
                
                if privilages is not None:
                    columns.append("privilages")
                    values.append(privilages)
                    placeholders.append("%s")
                
                if rank is not None:
                    columns.append("rank")
                    values.append(rank)
                    placeholders.append("%s")
                
                if created_at is not None:
                    columns.append("created_at")
                    values.append(created_at)
                    placeholders.append("%s")
                
                if updated_at is not None:
                    columns.append("updated_at")
                    values.append(updated_at)
                    placeholders.append("%s")
                
                if not columns:
                    raise ValueError("At least one field must be provided")
                
                query = f"INSERT INTO users ({', '.join(columns)}) VALUES ({', '.join(placeholders)}) RETURNING *"
                await cur.execute(query, values)
                result = await cur.fetchone()
                
                if result:
                    # Convert result to dictionary
                    column_names = [desc[0] for desc in cur.description]
                    return dict(zip(column_names, result))
                else:
                    return {"error": "Failed to create user"}
                
    except Exception as e:
        return {"error": str(e)}


async def read_users(
    user_id: Optional[str] = None,
    email: Optional[str] = None,
    registration_number: Optional[str] = None,
    name: Optional[str] = None,
    group: Optional[int] = None,
    course: Optional[str] = None,
    year_of_study: Optional[int] = None,
    time_to_allotment: Optional[int] = None,
    is_alloted: Optional[bool] = None,
    mobile_number: Optional[str] = None,
    role: Optional[str] = None,
    privilages: Optional[List[str]] = None,
    rank: Optional[int] = None,
    created_at: Optional[int] = None,
    updated_at: Optional[int] = None,
    limit: Optional[int] = None,
    offset: Optional[int] = None,
) -> Dict[str, Any]:
    """Read users from the database with optional filters."""
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
                
                if email is not None:
                    where_conditions.append("email = %s")
                    values.append(email)
                
                if registration_number is not None:
                    where_conditions.append("registration_number = %s")
                    values.append(registration_number)
                
                if name is not None:
                    where_conditions.append("name ILIKE %s")
                    values.append(f"%{name}%")
                
                if group is not None:
                    where_conditions.append("group = %s")
                    values.append(group)
                if course is not None:
                    where_conditions.append("course ILIKE %s")
                    values.append(f"%{course}%")
                
                if year_of_study is not None:
                    where_conditions.append("year_of_study = %s")
                    values.append(year_of_study)
                
                if time_to_allotment is not None:
                    where_conditions.append("time_to_allotment = %s")
                    values.append(time_to_allotment)
                
                if is_alloted is not None:
                    where_conditions.append("is_alloted = %s")
                    values.append(is_alloted)
                
                if mobile_number is not None:
                    where_conditions.append("mobile_number = %s")
                    values.append(mobile_number)
                
                if role is not None:
                    where_conditions.append("role = %s")
                    values.append(role)
                
                if privilages is not None:
                    where_conditions.append("privilages @> %s")
                    values.append(privilages)
                
                if rank is not None:
                    where_conditions.append("rank = %s")
                    values.append(rank)
                
                if created_at is not None:
                    where_conditions.append("created_at = %s")
                    values.append(created_at)
                
                if updated_at is not None:
                    where_conditions.append("updated_at = %s")
                    values.append(updated_at)
                
                # Build the query
                query = "SELECT * FROM users"
                if where_conditions:
                    query += " WHERE " + " AND ".join(where_conditions)
                
                query += " ORDER BY created_at DESC"
                
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


async def update_user(
    user_id: str,
    email: Optional[str] = None,
    registration_number: Optional[str] = None,
    name: Optional[str] = None,
    group: Optional[int] = None,
    course: Optional[str] = None,
    year_of_study: Optional[int] = None,
    time_to_allotment: Optional[int] = None,
    is_alloted: Optional[bool] = None,
    mobile_number: Optional[str] = None,
    role: Optional[str] = None,
    privilages: Optional[List[str]] = None,
    rank: Optional[int] = None,
    created_at: Optional[int] = None,
    updated_at: Optional[int] = None,
) -> Dict[str, Any]:
    """Update a user in the database using user_id as identifier."""
    connection_pool = await get_connection_pool_async()
    
    try:
        async with connection_pool.connection() as conn:
            async with conn.cursor() as cur:
                # Build SET clause for fields that are provided
                set_clauses = []
                values = []
                
                if email is not None:
                    set_clauses.append("email = %s")
                    values.append(email)
                
                if registration_number is not None:
                    set_clauses.append("registration_number = %s")
                    values.append(registration_number)
                
                if name is not None:
                    set_clauses.append("name = %s")
                    values.append(name)
                
                if group is not None:
                    set_clauses.append("group = %s")
                    values.append(group)
                
                if course is not None:
                    set_clauses.append("course = %s")
                    values.append(course)
                
                if year_of_study is not None:
                    set_clauses.append("year_of_study = %s")
                    values.append(year_of_study)
                
                if time_to_allotment is not None:
                    set_clauses.append("time_to_allotment = %s")
                    values.append(time_to_allotment)
                
                if is_alloted is not None:
                    set_clauses.append("is_alloted = %s")
                    values.append(is_alloted)
                
                if mobile_number is not None:
                    set_clauses.append("mobile_number = %s")
                    values.append(mobile_number)
                if role is not None:
                    set_clauses.append("role = %s")
                    values.append(role)
                
                if privilages is not None:
                    set_clauses.append("privilages = %s")
                    values.append(privilages)
                
                if rank is not None:
                    set_clauses.append("rank = %s")
                    values.append(rank)
                
                if created_at is not None:
                    set_clauses.append("created_at = %s")
                    values.append(created_at)
                
                if updated_at is not None:
                    set_clauses.append("updated_at = %s")
                    values.append(updated_at)
                
                if not set_clauses:
                    raise ValueError("At least one field must be provided for update")
                
                # Add user_id to values
                values.append(user_id)
                
                query = f"UPDATE users SET {', '.join(set_clauses)} WHERE user_id = %s RETURNING *"
                await cur.execute(query, values)
                result = await cur.fetchone()
                
                if result:
                    column_names = [desc[0] for desc in cur.description]
                    return dict(zip(column_names, result))
                else:
                    return {"error": "User not found or update failed"}
                
    except Exception as e:
        return {"error": str(e)}


async def delete_user(
    user_id: str
) -> Dict[str, Any]:
    """Delete a user from the database using user_id."""
    connection_pool = await get_connection_pool_async()
    
    try:
        async with connection_pool.connection() as conn:
            async with conn.cursor() as cur:
                query = "DELETE FROM users WHERE user_id = %s RETURNING *"
                await cur.execute(query, [user_id])
                result = await cur.fetchone()
                
                if result:
                    column_names = [desc[0] for desc in cur.description]
                    return {
                        "deleted": True,
                        "data": dict(zip(column_names, result))
                    }
                else:
                    return {"error": "User not found"}
                
    except Exception as e:
        return {"error": str(e)}
