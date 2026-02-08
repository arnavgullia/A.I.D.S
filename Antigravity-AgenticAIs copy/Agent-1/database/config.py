"""
Database Configuration for Agent 1.

SWITCHING TO MYSQL (When teammate's database is ready):
========================================================

1. Install MySQL connector:
   pip install mysql-connector-python

2. Update DB_CONFIG below with your MySQL credentials:
   DB_CONFIG = {
       "type": "mysql",
       "host": "localhost",
       "port": 3306,
       "database": "aegis_asteroids",
       "user": "your_username",
       "password": "your_password"
   }

3. The connection.py file will auto-detect and use MySQL when configured.

CURRENT CONFIGURATION:
=====================
Using SQLite for development/testing.
"""

# Database configuration
DB_CONFIG = {
    # Set to "mysql" when teammate's database is ready
    "type": "sqlite",  # Options: "sqlite" or "mysql"
    
    # SQLite settings (current)
    "sqlite_path": "asteroids.db",  # Relative to database/ folder
    
    # MySQL settings (uncomment and fill when ready)
    # "host": "localhost",
    # "port": 3306,
    # "database": "aegis_asteroids",
    # "user": "your_username",
    # "password": "your_password",
}


def get_db_type() -> str:
    """Get the configured database type."""
    return DB_CONFIG.get("type", "sqlite")


def is_mysql() -> bool:
    """Check if MySQL is configured."""
    return get_db_type() == "mysql"


def is_sqlite() -> bool:
    """Check if SQLite is configured."""
    return get_db_type() == "sqlite"
