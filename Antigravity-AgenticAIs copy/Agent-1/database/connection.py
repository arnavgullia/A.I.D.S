"""
Database connection utilities for Agent 1.
Provides simple interface for querying asteroid data.
"""

import sqlite3
from typing import Dict, List, Optional, Any
from contextlib import contextmanager
from .models import get_db_path


@contextmanager
def get_connection():
    """Context manager for database connections."""
    conn = sqlite3.connect(get_db_path())
    conn.row_factory = sqlite3.Row  # Enable dict-like access
    try:
        yield conn
    finally:
        conn.close()


def row_to_dict(row: sqlite3.Row) -> Dict[str, Any]:
    """Convert a database row to a dictionary."""
    return dict(row)


def get_asteroid_by_id(asteroid_id: str) -> Optional[Dict[str, Any]]:
    """
    Retrieve an asteroid by its ID.
    
    Args:
        asteroid_id: The unique identifier of the asteroid
        
    Returns:
        Dictionary with asteroid properties, or None if not found
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM asteroids WHERE id = ?", (asteroid_id,))
        row = cursor.fetchone()
        return row_to_dict(row) if row else None


def get_asteroid_by_name(name: str) -> Optional[Dict[str, Any]]:
    """
    Retrieve an asteroid by its name (case-insensitive partial match).
    
    Args:
        name: The name of the asteroid to search for
        
    Returns:
        Dictionary with asteroid properties, or None if not found
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM asteroids WHERE LOWER(name) LIKE LOWER(?)",
            (f"%{name}%",)
        )
        row = cursor.fetchone()
        return row_to_dict(row) if row else None


def get_all_asteroids() -> List[Dict[str, Any]]:
    """
    Retrieve all asteroids from the database.
    
    Returns:
        List of asteroid dictionaries
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM asteroids ORDER BY impact_probability DESC")
        rows = cursor.fetchall()
        return [row_to_dict(row) for row in rows]


def search_asteroids(
    min_diameter: Optional[float] = None,
    max_diameter: Optional[float] = None,
    min_velocity: Optional[float] = None,
    max_velocity: Optional[float] = None,
    min_impact_probability: Optional[float] = None,
    max_impact_probability: Optional[float] = None,
    max_days_until_approach: Optional[int] = None,
    composition: Optional[str] = None,
    is_potentially_hazardous: Optional[bool] = None,
    limit: int = 100
) -> List[Dict[str, Any]]:
    """
    Search asteroids with flexible filter criteria.
    
    Args:
        min_diameter: Minimum diameter in meters
        max_diameter: Maximum diameter in meters
        min_velocity: Minimum velocity in km/s
        max_velocity: Maximum velocity in km/s
        min_impact_probability: Minimum impact probability (0-1)
        max_impact_probability: Maximum impact probability (0-1)  
        max_days_until_approach: Maximum days until closest approach
        composition: Filter by composition type
        is_potentially_hazardous: Filter by PHA status
        limit: Maximum number of results to return
        
    Returns:
        List of matching asteroid dictionaries
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        
        conditions = []
        params = []
        
        if min_diameter is not None:
            conditions.append("diameter >= ?")
            params.append(min_diameter)
        if max_diameter is not None:
            conditions.append("diameter <= ?")
            params.append(max_diameter)
        if min_velocity is not None:
            conditions.append("velocity >= ?")
            params.append(min_velocity)
        if max_velocity is not None:
            conditions.append("velocity <= ?")
            params.append(max_velocity)
        if min_impact_probability is not None:
            conditions.append("impact_probability >= ?")
            params.append(min_impact_probability)
        if max_impact_probability is not None:
            conditions.append("impact_probability <= ?")
            params.append(max_impact_probability)
        if max_days_until_approach is not None:
            conditions.append("days_until_approach <= ?")
            params.append(max_days_until_approach)
        if composition is not None:
            conditions.append("LOWER(composition) = LOWER(?)")
            params.append(composition)
        if is_potentially_hazardous is not None:
            conditions.append("is_potentially_hazardous = ?")
            params.append(1 if is_potentially_hazardous else 0)
        
        query = "SELECT * FROM asteroids"
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        query += " ORDER BY impact_probability DESC"
        query += f" LIMIT {limit}"
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        return [row_to_dict(row) for row in rows]


def count_asteroids() -> int:
    """Get total count of asteroids in database."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM asteroids")
        return cursor.fetchone()[0]
