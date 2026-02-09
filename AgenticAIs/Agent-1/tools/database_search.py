"""
Database Search Tool for Agent 1.
Finds asteroids matching specified criteria.
"""

from typing import Optional, Dict, Any, List
from langchain_core.tools import tool

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from database.connection import search_asteroids


@tool
def database_search_tool(
    min_diameter: Optional[float] = None,
    max_diameter: Optional[float] = None,
    min_velocity: Optional[float] = None,
    max_velocity: Optional[float] = None,
    min_impact_probability: Optional[float] = None,
    max_impact_probability: Optional[float] = None,
    max_days_until_approach: Optional[int] = None,
    composition: Optional[str] = None,
    threat_level: Optional[str] = None
) -> Dict[str, Any]:
    """
    Search for asteroids matching specific criteria.
    
    Use this tool when the user wants to find multiple asteroids based on
    conditions like size, threat level, approaching soon, etc.
    
    Args:
        min_diameter: Minimum diameter in meters (e.g., 100 for asteroids >= 100m)
        max_diameter: Maximum diameter in meters
        min_velocity: Minimum velocity in km/s
        max_velocity: Maximum velocity in km/s
        min_impact_probability: Minimum impact probability (0.0 to 1.0)
        max_impact_probability: Maximum impact probability (0.0 to 1.0)
        max_days_until_approach: Maximum days until closest approach (e.g., 365 for within 1 year)
        composition: Filter by composition type ('stony', 'iron', 'carbonaceous', etc.)
        threat_level: Filter by threat classification ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL')
    
    Returns:
        A dictionary with:
        - count: Number of matching asteroids
        - filters_applied: The criteria used for filtering
        - asteroids: List of matching asteroids with key properties
    """
    # Convert threat_level to probability range
    if threat_level:
        threat_ranges = {
            "LOW": (0.0, 0.1),
            "MEDIUM": (0.1, 0.5),
            "HIGH": (0.5, 0.8),
            "CRITICAL": (0.8, 1.0)
        }
        if threat_level.upper() in threat_ranges:
            prob_min, prob_max = threat_ranges[threat_level.upper()]
            if min_impact_probability is None:
                min_impact_probability = prob_min
            if max_impact_probability is None:
                max_impact_probability = prob_max
    
    results = search_asteroids(
        min_diameter=min_diameter,
        max_diameter=max_diameter,
        min_velocity=min_velocity,
        max_velocity=max_velocity,
        min_impact_probability=min_impact_probability,
        max_impact_probability=max_impact_probability,
        max_days_until_approach=max_days_until_approach,
        composition=composition
    )
    
    # Format results
    formatted = []
    for a in results:
        # Classify threat level for output
        prob = a["impact_probability"]
        if prob >= 0.8:
            level = "CRITICAL"
        elif prob >= 0.5:
            level = "HIGH"
        elif prob >= 0.1:
            level = "MEDIUM"
        else:
            level = "LOW"
        
        formatted.append({
            "id": a["id"],
            "name": a["name"],
            "diameter_m": a["diameter"],
            "velocity_km_s": a["velocity"],
            "impact_probability": prob,
            "threat_level": level,
            "days_until_approach": a["days_until_approach"],
            "composition": a["composition"]
        })
    
    # Build filters applied summary
    filters = {}
    if min_diameter: filters["min_diameter"] = min_diameter
    if max_diameter: filters["max_diameter"] = max_diameter
    if min_velocity: filters["min_velocity"] = min_velocity
    if max_velocity: filters["max_velocity"] = max_velocity
    if min_impact_probability: filters["min_impact_probability"] = min_impact_probability
    if max_impact_probability: filters["max_impact_probability"] = max_impact_probability
    if max_days_until_approach: filters["max_days_until_approach"] = max_days_until_approach
    if composition: filters["composition"] = composition
    if threat_level: filters["threat_level"] = threat_level
    
    return {
        "count": len(formatted),
        "filters_applied": filters if filters else "none (returned all asteroids)",
        "asteroids": formatted
    }
