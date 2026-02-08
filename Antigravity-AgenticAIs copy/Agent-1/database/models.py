"""
Database models and schema for asteroid data.
Uses SQLite for simplicity and portability.
"""

import sqlite3
import os
from pathlib import Path


# Database path - stored in the Agent-1 directory
DB_PATH = Path(__file__).parent / "asteroids.db"


def get_db_path() -> str:
    """Get the absolute path to the database file."""
    return str(DB_PATH)


def init_database():
    """Initialize the database with the asteroid schema."""
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()
    
    # Create asteroids table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS asteroids (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            diameter REAL NOT NULL,          -- meters
            mass REAL NOT NULL,              -- kg
            velocity REAL NOT NULL,          -- km/s
            composition TEXT NOT NULL,       -- stony, iron, carbonaceous, etc.
            impact_probability REAL NOT NULL, -- 0.0 to 1.0
            days_until_approach INTEGER NOT NULL,
            semi_major_axis REAL,            -- AU (Astronomical Units)
            eccentricity REAL,               -- orbital eccentricity
            inclination REAL,                -- degrees
            discovery_date TEXT,             -- ISO format date
            last_observation TEXT,           -- ISO format date
            observation_arc_days INTEGER,    -- days of observation
            absolute_magnitude REAL,         -- H value
            albedo REAL,                     -- reflectivity 0.0 to 1.0
            rotation_period REAL,            -- hours
            spectral_type TEXT,              -- taxonomic classification
            is_potentially_hazardous INTEGER DEFAULT 1,  -- boolean as int
            notes TEXT
        )
    """)
    
    conn.commit()
    conn.close()
    print(f"Database initialized at: {get_db_path()}")


def drop_database():
    """Remove the database file if it exists."""
    if DB_PATH.exists():
        os.remove(DB_PATH)
        print(f"Database removed: {get_db_path()}")


if __name__ == "__main__":
    init_database()
