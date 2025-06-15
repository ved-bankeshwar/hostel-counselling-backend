import sys
import os
import asyncio
import psycopg

# Add the parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from dbconfig import get_connection_pool_async

# We'll get the connection pool in the create_tables function
connection_pool_async = None

table_definitions = {    "users": [
        "user_id VARCHAR(255) PRIMARY KEY DEFAULT gen_random_uuid()",
        "email VARCHAR(255) UNIQUE NOT NULL",
        "registration_number VARCHAR(255) UNIQUE NOT NULL",
        "name VARCHAR(255) NOT NULL",
        "group INTEGER NOT NULL",
        "course VARCHAR(255) NOT NULL",
        "year_of_study INTEGER NOT NULL",
        "time_to_allotment BIGINT DEFAULT (EXTRACT(EPOCH FROM CURRENT_TIMESTAMP AT TIME ZONE 'UTC'))",
        "is_alloted BOOLEAN DEFAULT FALSE",
        "mobile_number VARCHAR(100)",
        "role VARCHAR(100)",
        "privilages VARCHAR[]",
        "rank INTEGER",
        "created_at BIGINT DEFAULT (EXTRACT(EPOCH FROM CURRENT_TIMESTAMP AT TIME ZONE 'UTC'))",
        "updated_at BIGINT DEFAULT (EXTRACT(EPOCH FROM CURRENT_TIMESTAMP AT TIME ZONE 'UTC'))",
    ],
    "blocks": [
        "block_letter VARCHAR(255) PRIMARY KEY",
        "block_name VARCHAR(10) NOT NULL",
        "is_deluxe BOOLEAN DEFAULT FALSE",
        "is_ac BOOLEAN DEFAULT FALSE",

    ],
    "floors": [
        "floor_id SERIAL PRIMARY KEY",
        "floor_number INTEGER NOT NULL",
        "block_letter FOREIGN KEY REFERENCES blocks(block_letter)",
    ],
    "rooms": [
        "room_number VARCHAR(10) PRIMARY KEY",
        "block_name VARCHAR(255) NOT NULL",
        "block_letter FOREIGN KEY REFERENCES blocks(block_letter)",
        "total_beds INTEGER DEFAULT 0",
        "floor_id REFERENCES floors(floor_id)",
    ],
    
    "friends": [
        "user_id FOREIGN KEY REFERENCES users(user_id)",
        "friend_id FOREIGN KEY REFERENCES users(user_id)",
    ],
    "allotments": [
        "allotment_id SERIAL PRIMARY KEY",
        "user_id FOREIGN KEY REFERENCES users(user_id)",
        "block_letter FOREIGN KEY REFERENCES blocks(block_letter)",
        "room_number FOREIGN KEY REFERENCES rooms(room_number)",
        "allotment_date BIGINT DEFAULT (EXTRACT(EPOCH FROM CURRENT_TIMESTAMP AT TIME ZONE 'UTC'))",
        "is_alloted BOOLEAN DEFAULT FALSE",
    ],
    "tenants": [
        "user_id FOREIGN KEY REFERENCES users(user_id)",
        "room_number FOREIGN KEY REFERENCES rooms(room_number)",
        "block_letter FOREIGN KEY REFERENCES blocks(block_letter)",
        "allotment_id FOREIGN KEY REFERENCES allotments(allotment_id)",
    ],
    

}


async def create_tables():
    """Create or alter tables in the PostgreSQL database."""
    global table_definitions, connection_pool_async

    # Get the connection pool
    connection_pool_async = await get_connection_pool_async()
    print("Connection pool obtained.")

    try:
        async with connection_pool_async.connection() as conn:
            print("Connected to the database.")
            async with conn.cursor() as cur:
                for table_name, table_definition in table_definitions.items():
                    print(f"Processing table: {table_name}")
                    # Check if the table exists
                    await cur.execute(
                        "SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = %s)",
                        (table_name,),
                    )
                    table_exists = (await cur.fetchone())[0]
                    print(f"Table {table_name} exists: {table_exists}")

                    if table_exists:
                        # Table exists, compare columns and update as needed
                        await cur.execute(
                            "SELECT column_name, data_type FROM information_schema.columns WHERE table_name = %s",
                            (table_name,),
                        )
                        existing_columns = {
                            row[0]: row[1] for row in await cur.fetchall()
                        }
                        print(f"Existing columns for {table_name}: {existing_columns}")

                        for column_definition in table_definition:
                            column_name = column_definition.split()[0]
                            column_data_type = column_definition.split()[1]
                            print(
                                f"Checking column: {column_name} with data type: {column_data_type}"
                            )

                            if column_name not in existing_columns:
                                # Column does not exist, add it
                                alter_table_query = f"ALTER TABLE {table_name} ADD COLUMN {column_definition}"
                                await cur.execute(alter_table_query)
                                print(f"Added column {column_name} to {table_name}")
                            elif existing_columns[column_name] != column_data_type:
                                # Column exists but has a different type, update it
                                # Skip ALTER if the data type is SERIAL
                                if column_data_type != "SERIAL":
                                    alter_table_query = f"ALTER TABLE {table_name} ALTER COLUMN {column_name} TYPE {column_data_type}"
                                    await cur.execute(alter_table_query)
                                    print(
                                        f"Updated column {column_name} in {table_name}"
                                    )
                    else:
                        # Table does not exist, create it
                        create_table_query = (
                            f"CREATE TABLE {table_name} ({', '.join(table_definition)})"
                        )
                        await cur.execute(create_table_query)
                        print(f"Created table {table_name}")

        # Commit the changes
        await conn.commit()
        print("Changes committed successfully.")
    except (Exception, psycopg.DatabaseError) as error:
        print(f"Error occurred: {error}")
        return {"error": error}


async def drop_tables():
    """Drop all tables in the PostgreSQL database."""
    global connection_pool_async

    # Ensure we have a connection pool
    if connection_pool_async is None:
        connection_pool_async = await get_connection_pool_async()

    table_names = [table_name for table_name in table_definitions.keys()]

    try:
        # Connect to the PostgreSQL server
        async with connection_pool_async.connection() as conn:
            async with conn.cursor() as cur:
                for table_name in table_names:
                    print(f"Dropping table: {table_name}")
                    drop_table_query = f"DROP TABLE IF EXISTS {table_name} CASCADE"
                    await cur.execute(drop_table_query)
                    print(f"Dropped table: {table_name}")

        # Commit the changes
        await conn.commit()
    except (Exception, psycopg.DatabaseError) as error:
        print(error)
        return {"error": error}


async def main():
    # user_id = "14cf4130-bf34-49b2-83d9-b3cd501d2da2"
    await drop_tables()
    await create_tables()
    # print(user_id)


if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    else:
        try:
            import uvloop

            uvloop.install()
        except Exception:
            pass
    asyncio.run(main())
