"""
Data Formatter Tool for Agent 1.
Formats asteroid data for Agent 2 and quantum system.
Generates exactly 16 parameter combinations for quantum Grover's algorithm.
"""

from typing import Dict, Any, List
from langchain_core.tools import tool
from datetime import datetime
import itertools


# Quantum algorithm constraint: Grover's works with 2^n items
# 16 = 2^4 is optimal for the teammate's implementation
QUANTUM_PARAMETER_COUNT = 16


def generate_deflection_parameters(asteroid_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Generate 16 deflection parameter combinations for quantum optimization.
    
    Creates a parameter space by varying:
    - Deflection angle (4 options)
    - Impact velocity (2 options)  
    - Timing (2 options)
    = 4 × 2 × 2 = 16 combinations
    """
    mass = asteroid_data.get("mass", 1e10)
    velocity = asteroid_data.get("velocity", 25.0)
    diameter = asteroid_data.get("diameter", 300)
    days_until = asteroid_data.get("days_until_approach", 180)
    composition = asteroid_data.get("composition", "stony")
    
    # Get composition factor for calculations
    comp_factor = _get_composition_factor(composition)
    
    # Calculate base deflection velocity needed (simplified physics)
    # Higher mass needs higher velocity, iron needs more force
    base_velocity = 5.0 * (mass / 1e10) ** 0.2 * comp_factor
    
    # Parameter variations
    angles = [15.0, 30.0, 45.0, 60.0]  # 4 deflection angles (degrees)
    velocities = [base_velocity * 0.8, base_velocity * 1.2]  # 2 velocity options
    timings = [0.6, 0.8]  # 2 timing options (fraction of available time)
    
    # Generate all 16 combinations
    parameters = []
    param_id = 0
    
    for angle, vel, timing in itertools.product(angles, velocities, timings):
        # Calculate mission timing
        mission_days = int(days_until * timing)
        impact_date_offset = days_until - mission_days
        
        # Estimate deflection distance (simplified)
        deflection_km = vel * mission_days * 0.1  # Rough approximation
        
        parameters.append({
            "param_id": param_id,
            "deflection_angle_deg": angle,
            "impact_velocity_km_s": round(vel, 2),
            "mission_timing_days": mission_days,
            "impact_date_offset_days": impact_date_offset,
            "estimated_deflection_km": round(deflection_km, 1),
            "composition_factor": comp_factor,
            "energy_factor": round(vel ** 2 * angle / 45, 2)
        })
        param_id += 1
    
    return parameters


@tool
def data_formatter_tool(asteroid_data: Dict[str, Any], include_threat_assessment: bool = True) -> Dict[str, Any]:
    """
    Format asteroid data for Agent 2 (Strategic Planner) or quantum system.
    
    Generates exactly 16 deflection parameter combinations optimized for
    Grover's quantum search algorithm. Each combination varies angle,
    velocity, and timing to find the optimal deflection approach.
    
    Use this tool when preparing to hand off data to Agent 2 for deflection
    strategy generation, or when formatting data for the quantum optimization system.
    
    Args:
        asteroid_data: Dictionary containing asteroid properties from database_query_tool
        include_threat_assessment: Whether to include threat classification (default True)
    
    Returns:
        Standardized JSON structure ready for Agent 2 or quantum system with:
        - asteroid_properties: Complete physical and orbital data
        - threat_classification: Threat level and impact probability
        - quantum_parameter_space: EXACTLY 16 parameter combinations for Grover's algorithm
        - metadata: Timestamp, source, and data version info
    """
    # Validate input data
    required_fields = ["id", "name", "mass", "velocity", "diameter"]
    missing = [f for f in required_fields if f not in asteroid_data]
    
    if missing:
        return {
            "error": f"Missing required fields: {missing}",
            "status": "INCOMPLETE_DATA",
            "suggestion": "Use database_query_tool to get complete asteroid data first"
        }
    
    # Extract core properties
    asteroid_id = asteroid_data.get("id")
    name = asteroid_data.get("name")
    mass = asteroid_data.get("mass")
    velocity = asteroid_data.get("velocity")
    diameter = asteroid_data.get("diameter")
    composition = asteroid_data.get("composition", "unknown")
    impact_prob = asteroid_data.get("impact_probability", 0)
    days_until = asteroid_data.get("days_until_approach", 0)
    
    # Orbital parameters
    orbital = {
        "semi_major_axis_au": asteroid_data.get("semi_major_axis"),
        "eccentricity": asteroid_data.get("eccentricity"),
        "inclination_deg": asteroid_data.get("inclination")
    }
    
    # Physical properties
    physical = {
        "diameter_m": diameter,
        "mass_kg": mass,
        "velocity_km_s": velocity,
        "composition": composition,
        "albedo": asteroid_data.get("albedo"),
        "rotation_period_hours": asteroid_data.get("rotation_period"),
        "spectral_type": asteroid_data.get("spectral_type")
    }
    
    # Threat classification
    if impact_prob >= 0.8:
        threat_level = "CRITICAL"
    elif impact_prob >= 0.5:
        threat_level = "HIGH"
    elif impact_prob >= 0.1:
        threat_level = "MEDIUM"
    else:
        threat_level = "LOW"
    
    threat = {
        "level": threat_level,
        "impact_probability": impact_prob,
        "days_until_approach": days_until,
        "deflection_required": threat_level in ["HIGH", "CRITICAL"]
    }
    
    # Generate exactly 16 quantum-compatible parameter combinations
    quantum_params = generate_deflection_parameters(asteroid_data)
    
    # Metadata
    metadata = {
        "formatted_at": datetime.utcnow().isoformat() + "Z",
        "source": "agent_1_database_intel",
        "data_version": "2.0",
        "asteroid_id": asteroid_id,
        "format_type": "quantum_grover_compatible",
        "parameter_count": len(quantum_params),
        "quantum_constraint": "Exactly 16 parameters for Grover's algorithm (2^4)"
    }
    
    result = {
        "status": "READY_FOR_QUANTUM",
        "asteroid_id": asteroid_id,
        "asteroid_name": name,
        "physical_properties": physical,
        "orbital_parameters": orbital,
        "quantum_parameter_space": quantum_params,  # Exactly 16 items!
        "metadata": metadata
    }
    
    if include_threat_assessment:
        result["threat_assessment"] = threat
    
    return result


def _get_composition_factor(composition: str) -> float:
    """
    Get a numerical factor for composition affecting deflection difficulty.
    Iron is harder to deflect than rubble pile.
    """
    composition_factors = {
        "iron": 1.5,        # Dense, hard to deflect
        "stony-iron": 1.3,  # Mixed
        "stony": 1.0,       # Standard
        "rocky": 1.0,       # Standard
        "carbonaceous": 0.8, # Softer, may fragment
        "rubble": 0.7,      # Rubble pile, easier deflection
        "unknown": 1.0
    }
    return composition_factors.get(composition.lower(), 1.0)

