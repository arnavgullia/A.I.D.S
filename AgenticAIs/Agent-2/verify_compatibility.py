"""
Verification Script: Project Aegis Compatibility Check
Verifies flow: Agent 1 Output -> Agent 2 -> Quantum Algorithm Input
"""

import sys
import os
import json
from dotenv import load_dotenv

# Ensure we can import local modules
# Add the current directory to sys.path
sys.path.append(os.getcwd())

# Attempt to load .env from current directory
load_dotenv()

from agent_2_strategic_planner import StrategicPlanner

def test_compatibility():
    print("RUNNING COMPATIBILITY CHECK...")
    
    # 1. Simulate Agent 1 Output (Formatted Data)
    # This matches the structure output by Agent 1's data_formatter_tool
    agent_1_output = {
        "status": "READY_FOR_QUANTUM",
        "asteroid_id": "APO-99942",
        "asteroid_name": "Apophis",
        "physical_properties": {
            "diameter_m": 340,
            "mass_kg": 6.1e10,
            "velocity_km_s": 30.7,
            "composition": "Stony",
            "albedo": 0.23,
            "rotation_period_hours": 30.0,
            "spectral_type": "S"
        },
        "orbital_parameters": {
            "semi_major_axis_au": 0.922,
            "eccentricity": 0.191,
            "inclination_deg": 3.33
        },
        "threat_assessment": {
            "level": "CRITICAL",
            "impact_probability": 0.027,
            "days_until_approach": 1050,
            "deflection_required": True
        },
        "quantum_parameter_space": [
            # Agent 2 should be able to handle this list of 16 items
            {"param_id": 0, "deflection_angle_deg": 15.0, "impact_velocity_km_s": 24.0, "mission_timing_days": 630, "estimated_deflection_km": 15000.0},
            {"param_id": 1, "deflection_angle_deg": 15.0, "impact_velocity_km_s": 36.0, "mission_timing_days": 630, "estimated_deflection_km": 22000.0},
            # ... (truncated for brevity, Agent 2 should handle the full list)
        ],
        "metadata": {
            "source": "agent_1_database_intel",
            "data_version": "2.0"
        }
    }
    
    # IMPORTANT: Agent 2 currently expects a simpler "flat" structure in its main demo loop,
    # OR it needs to be intelligent enough to parse this nested structure.
    # The StrategicPlanner.plan_mission method takes a dict.
    # Let's see if the LLM can handle the nested dict.
    
    print(f"\n[1] Agent 1 Output Received (Simulated):\n{json.dumps(agent_1_output, indent=2)}")
    
    # 2. Run Agent 2 (Strategic Planner)
    print("\n[2] Agent 2 Processing...")
    
    # Check API Key
    if not os.getenv("AGENT2_GOOGLE_API_KEY") and not os.getenv("GOOGLE_API_KEY"):
         print("❌ SKIPPING: No API Key found in environment.")
         return

    try:
        planner = StrategicPlanner(model="gemini-2.0-flash")
        result = planner.plan_mission(agent_1_output)
    except Exception as e:
        print(f"❌ Agent 2 Failed: {e}")
        import traceback
        traceback.print_exc()
        return

    print(f"\n[3] Agent 2 Final Output (Quantum Handoff):\n{json.dumps(result, indent=2)}")
    
    # 3. Verify Quantum Contract
    print("\n[4] Verifying Quantum Contract...")
    errors = []
    
    if not isinstance(result, dict):
        print("❌ CRITICAL: Result is not a dictionary.")
        return

    # Check Top Level Keys
    required_keys = ["status", "target", "selected_strategy", "search_parameters", "dataset_path"]
    for key in required_keys:
        if key not in result:
            errors.append(f"Missing key: {key}")
            
    if result.get("status") != "READY_FOR_QUANTUM":
        errors.append(f"Invalid status: {result.get('status')}")
        
    dataset_path = result.get("dataset_path")
    if not dataset_path:
        errors.append("Dataset path is empty.")
    elif not os.path.exists(dataset_path):
        errors.append(f"Dataset file not found at: {dataset_path}")
    else:
        # Check Dataset Content
        try:
            with open(dataset_path, 'r') as f:
                candidates = json.load(f)
                
            if len(candidates) != 16:
                errors.append(f"Quantum Constraint Violation: Expected 16 candidates, found {len(candidates)}")
                
            # Check Candidate Fields
            if candidates:
                cand = candidates[0]
                rec_cand_keys = ["id", "velocity_km_s", "angle_degrees"]
                for k in rec_cand_keys:
                    if k not in cand:
                         errors.append(f"Candidate missing key: {k}")
                         
        except Exception as e:
            errors.append(f"Failed to read dataset: {e}")

    if not errors:
        print("\n✅ COMPATIBILITY VERIFIED: 100/100")
        print("Agent 2 correctly interprets Agent 1 data and produces valid Quantum Ready output.")
    else:
        print("\n❌ COMPATIBILITY FAILED:")
        for e in errors:
            print(f"- {e}")

if __name__ == "__main__":
    test_compatibility()
