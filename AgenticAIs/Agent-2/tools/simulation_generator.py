"""
Simulation Generator Tool for Agent 2.
Generates candidate deflection missions for the Quantum Agent to optimize.
"""

import json
import random
import os
from typing import Dict, List, Any
from langchain_core.tools import tool

# Constants
CANDIDATES_FILE = "candidates_generated.json"
DEFAULT_SAMPLE_SIZE = 16  # Quantum constraint (4 qubits)

@tool
def generate_simulation_space(
    strategy_type: str,
    min_velocity: float,
    max_velocity: float,
    min_angle: float,
    max_angle: float,
    sample_size: int = DEFAULT_SAMPLE_SIZE
) -> str:
    """
    Generates a list of potential deflection mission trajectories based on physical constraints.
    
    This tool acts as the "Calculator" for the "Brain" (Agent 2). It takes the
    strategic ranges defined by the Agent and generates specific simulation candidates.
    
    Args:
        strategy_type: "kinetic" (Impactor) or "gravity" (Tractor)
        min_velocity: Minimum impact speed (km/s)
        max_velocity: Maximum impact speed (km/s)
        min_angle: Minimum approach angle (degrees)
        max_angle: Maximum approach angle (degrees)
        sample_size: Number of candidates to generate (Default: 16)
        
    Returns:
        Path to the generated JSON file (candidates_generated.json)
    """
    print(f"\n[Tool] Generating {sample_size} candidates for strategy: {strategy_type.upper()}")
    print(f"[Tool] Velocity Range: {min_velocity} - {max_velocity} km/s")
    print(f"[Tool] Angle Range: {min_angle} - {max_angle} degrees")
    
    candidates = []
    
    for i in range(sample_size):
        # Generate random values within the strategic ranges
        velocity = random.uniform(min_velocity, max_velocity)
        angle = random.uniform(min_angle, max_angle)
        
        # Calculate a mock "deflection_efficiency" (conceptually this would be the output of a sim)
        # For the quantum agent, we just need the parameters. 
        # But we'll add an ID.
        
        candidate = {
            "id": i,
            "strategy": strategy_type,
            "velocity_km_s": round(velocity, 2),
            "angle_degrees": round(angle, 2),
            # Mock estimation parameters for the Quantum Oracle to evaluate later
            "estimated_impact_energy_kt": round(0.5 * 1000 * (velocity * 1000)**2 / 4.184e12, 2) # Rough KE calc for 1000kg probe
        }
        candidates.append(candidate)
        
    # Save to file
    output_path = os.path.join(os.getcwd(), CANDIDATES_FILE)
    
    # Check if we are in the Agent-2 directory, if not, try to save there
    if "Agent-2" not in os.getcwd():
         # Attempt to find Agent-2 path relative or absolute
         agent_2_path = "/home/pranjay/workspace/Antigravity-AgenticAIs/Agent-2"
         if os.path.exists(agent_2_path):
             output_path = os.path.join(agent_2_path, CANDIDATES_FILE)
    
    with open(output_path, "w") as f:
        json.dump(candidates, f, indent=2)
        
    print(f"[Tool] Saved {len(candidates)} candidates to {output_path}")
    return output_path
