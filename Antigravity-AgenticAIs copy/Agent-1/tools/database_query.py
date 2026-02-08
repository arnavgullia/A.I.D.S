"""
Database Query Tool for Agent 1.
Retrieves specific asteroid data by ID or name.
"""

from typing import Optional, Dict, Any
from langchain_core.tools import tool

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from database.connection import get_asteroid_by_id, get_asteroid_by_name, get_all_asteroids


@tool
def database_query_tool(identifier: str) -> Dict[str, Any]:
    """
    Retrieve detailed information about a specific asteroid.
    
    Use this tool when you need to get complete data about a single asteroid.
    You can query by asteroid ID (like 'APO2026') or by name (like 'Apophis').
    
    Args:
        identifier: The asteroid ID (e.g., 'APO2026') or name (e.g., 'Apophis-2026', 'Bennu')
    
    Returns:
        A dictionary containing all asteroid properties including:
        - id, name, diameter (meters), mass (kg), velocity (km/s)
        - composition, impact_probability, days_until_approach
        - orbital parameters, discovery info, and more
        
        Returns error message if asteroid not found.
    """
    # Try by ID first
    result = get_asteroid_by_id(identifier)
    
    if result is None:
        # Try by name
        result = get_asteroid_by_name(identifier)
    
    if result is None:
        return {
            "error": f"No asteroid found matching '{identifier}'",
            "suggestion": "Try using 'list_all_asteroids' to see available asteroids, or check the spelling."
        }
    
    return result


@tool
def list_all_asteroids() -> Dict[str, Any]:
    """
    List all asteroids in the database.
    
    Use this tool when the user asks to see all asteroids, or wants to know
    what asteroids are in the database.
    
    Returns:
        A dictionary with:
        - count: Total number of asteroids
        - asteroids: List of asteroid summaries (id, name, diameter, impact_probability)
    """
    all_asteroids = get_all_asteroids()
    
    # Return summary for each asteroid
    summaries = []
    for a in all_asteroids:
        summaries.append({
            "id": a["id"],
            "name": a["name"],
            "diameter_m": a["diameter"],
            "velocity_km_s": a["velocity"],
            "impact_probability": a["impact_probability"],
            "days_until_approach": a["days_until_approach"],
            "composition": a["composition"]
        })
    
    return {
        "count": len(summaries),
        "asteroids": summaries
    }
