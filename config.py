import os
from typing import Dict

def get_db_config() -> Dict[str, str]:
    """
    Get database configuration from environment variables.
    Falls back to local defaults if not in production.
    """
    # Check if we're on Render (or any production environment)
    database_url = os.getenv("DATABASE_URL")
    
    if database_url:
        # Parse DATABASE_URL for production (Render provides this)
        # Format: postgresql://user:password@host:port/database
        return parse_database_url(database_url)
    else:
        # Local development configuration
        return {
            "host": os.getenv("DB_HOST", "localhost"),
            "database": os.getenv("DB_NAME", "room_counselling"),
            "user": os.getenv("DB_USER", "admin"),
            "password": os.getenv("DB_PASSWORD", "admin123"),
            "port": int(os.getenv("DB_PORT", "5432"))
        }

def parse_database_url(url: str) -> Dict[str, str]:
    """Parse DATABASE_URL into psycopg2 connection parameters"""
    from urllib.parse import urlparse
    
    result = urlparse(url)
    
    return {
        "host": result.hostname,
        "database": result.path[1:],  # Remove leading slash
        "user": result.username,
        "password": result.password,
        "port": result.port or 5432
    }

# Export the configuration
DB_CONFIG = get_db_config()
