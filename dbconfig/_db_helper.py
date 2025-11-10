import psycopg2
import os

def get_db_config():
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        from urllib.parse import urlparse
        result = urlparse(database_url)
        return {
            "host": result.hostname,
            "database": result.path[1:],
            "user": result.username,
            "password": result.password,
            "port": result.port or 5432
        }
    return {
        "host": os.getenv("DB_HOST", "localhost"),
        "database": os.getenv("DB_NAME", "room_counselling"),
        "user": os.getenv("DB_USER", "admin"),
        "password": os.getenv("DB_PASSWORD", "admin123"),
        "port": int(os.getenv("DB_PORT", "5432"))
    }

def get_connection():
    return psycopg2.connect(**get_db_config())
