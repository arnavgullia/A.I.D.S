"""
Threat Calculator Tool for Agent 1.
Performs basic threat assessment calculations.
"""

from typing import Dict, Any
from langchain_core.tools import tool
import math


def calculate_impact_energy(mass_kg: float, velocity_km_s: float) -> Dict[str, float]:
    """
    Calculate kinetic energy of asteroid impact.
    
    E = 0.5 * m * v^2
    
    Returns energy in Joules and equivalent megatons of TNT.
    1 megaton TNT = 4.184 × 10^15 Joules
    """
    velocity_m_s = velocity_km_s * 1000  # Convert to m/s
    energy_joules = 0.5 * mass_kg * (velocity_m_s ** 2)
    
    MEGATON_TNT_JOULES = 4.184e15
    energy_megatons = energy_joules / MEGATON_TNT_JOULES
    
    return {
        "energy_joules": energy_joules,
        "energy_megatons_tnt": energy_megatons
    }


def estimate_crater_diameter(impact_energy_joules: float) -> float:
    """
    Estimate crater diameter based on impact energy.
    
    Simplified scaling law: D ~ E^0.25 (very approximate)
    This is a rough estimate for solid rock impacts.
    """
    # Rough empirical scaling for Earth impacts
    # D ≈ 0.07 * E^0.25 (km) for energy in Joules
    diameter_km = 0.07 * (impact_energy_joules ** 0.25)
    return diameter_km


def estimate_damage_radius(energy_megatons: float) -> Dict[str, float]:
    """
    Estimate damage radii based on impact energy.
    
    Returns approximate radii for different damage levels.
    """
    # Very simplified damage model
    # Fireball radius scales roughly with cube root of energy
    
    if energy_megatons < 1:
        return {
            "fireball_km": 1,
            "severe_damage_km": 5,
            "moderate_damage_km": 20,
            "description": "Local damage - similar to nuclear weapon"
        }
    elif energy_megatons < 100:
        return {
            "fireball_km": 5 * (energy_megatons ** 0.33),
            "severe_damage_km": 20 * (energy_megatons ** 0.33),
            "moderate_damage_km": 100 * (energy_megatons ** 0.33),
            "description": "City-destroying impact"
        }
    elif energy_megatons < 10000:
        return {
            "fireball_km": 10 * (energy_megatons ** 0.33),
            "severe_damage_km": 50 * (energy_megatons ** 0.33),
            "moderate_damage_km": 200 * (energy_megatons ** 0.33),
            "description": "Regional devastation - country-level destruction"
        }
    else:
        return {
            "fireball_km": 50 * (energy_megatons ** 0.33),
            "severe_damage_km": 200 * (energy_megatons ** 0.33),
            "moderate_damage_km": 1000 * (energy_megatons ** 0.33),
            "description": "Extinction-level event - global catastrophe"
        }


@tool
def threat_calculator_tool(asteroid_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calculate comprehensive threat assessment for an asteroid.
    
    Use this tool when you need to assess how dangerous an asteroid is.
    Provide the asteroid data dictionary from database_query_tool.
    
    Args:
        asteroid_data: Dictionary containing asteroid properties:
            - mass (kg): Required for energy calculation
            - velocity (km/s): Required for energy calculation
            - diameter (meters): Size of asteroid
            - impact_probability: Probability of Earth impact (0-1)
    
    Returns:
        Comprehensive threat assessment including:
        - threat_level: LOW, MEDIUM, HIGH, or CRITICAL
        - impact_energy: Energy in megatons TNT equivalent
        - estimated_damage: Description of potential damage
        - risk_score: Numerical risk assessment (0-100)
        - recommended_action: What should be done
    """
    # Extract required fields
    mass = asteroid_data.get("mass")
    velocity = asteroid_data.get("velocity")
    diameter = asteroid_data.get("diameter")
    impact_prob = asteroid_data.get("impact_probability", 0)
    name = asteroid_data.get("name", "Unknown")
    
    # Validate data
    if mass is None or velocity is None:
        return {
            "error": "Missing required data (mass or velocity)",
            "required_fields": ["mass", "velocity", "diameter", "impact_probability"]
        }
    
    # Calculate impact energy
    energy = calculate_impact_energy(mass, velocity)
    energy_mt = energy["energy_megatons_tnt"]
    
    # Estimate damage
    damage = estimate_damage_radius(energy_mt)
    
    # Calculate crater
    crater_km = estimate_crater_diameter(energy["energy_joules"])
    
    # Determine threat level based on energy and probability
    # Risk = Probability × Consequence
    consequence_score = min(100, math.log10(max(1, energy_mt)) * 20)
    risk_score = impact_prob * consequence_score
    
    if risk_score >= 70 or (impact_prob >= 0.8 and energy_mt > 100):
        threat_level = "CRITICAL"
        urgency = "IMMEDIATE"
        action = "EMERGENCY DEFLECTION REQUIRED - Recommend immediate handoff to Agent 2 for strategy generation"
    elif risk_score >= 40 or (impact_prob >= 0.5 and energy_mt > 10):
        threat_level = "HIGH"
        urgency = "URGENT"
        action = "DEFLECTION MISSION RECOMMENDED - Prepare data for Agent 2 strategic planning"
    elif risk_score >= 15 or (impact_prob >= 0.1):
        threat_level = "MEDIUM"
        urgency = "ELEVATED"
        action = "CLOSE MONITORING - Consider deflection planning, request additional observations"
    else:
        threat_level = "LOW"
        urgency = "ROUTINE"
        action = "STANDARD MONITORING - Continue observation, no deflection needed currently"
    
    return {
        "asteroid_name": name,
        "threat_level": threat_level,
        "urgency": urgency,
        "risk_score": round(risk_score, 2),
        "impact_analysis": {
            "impact_probability_percent": round(impact_prob * 100, 2),
            "impact_energy_megatons_tnt": round(energy_mt, 2),
            "estimated_crater_diameter_km": round(crater_km, 2),
            "damage_assessment": damage["description"]
        },
        "damage_radii": {
            "fireball_radius_km": round(damage.get("fireball_km", 0), 1),
            "severe_damage_radius_km": round(damage.get("severe_damage_km", 0), 1),
            "moderate_damage_radius_km": round(damage.get("moderate_damage_km", 0), 1)
        },
        "recommended_action": action,
        "next_steps": [
            "Verify observation data accuracy",
            "Update orbital calculations",
            f"{'Request Agent 2 deflection analysis' if threat_level in ['HIGH', 'CRITICAL'] else 'Continue standard monitoring'}"
        ]
    }
