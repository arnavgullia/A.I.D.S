"""Quick test of Agent 2"""
import sys
sys.path.append('/home/pranjay/workspace/Antigravity-AgenticAIs/Agent-2')

from agent_2_strategic_planner import StrategicPlanner
import json

print("Initializing Agent 2...")
planner = StrategicPlanner(model="gemini-2.0-flash")

# Test data (Apophis - should be Kinetic)
test_data = {
    "name": "Apophis-99942",
    "diameter_m": 340,
    "mass_kg": 6.1e10,
    "velocity_km_s": 30.7,
    "impact_probability": 0.027,
    "days_until_approach": 1050,
    "composition": "Stony"
}

print("\nTest Data:")
print(json.dumps(test_data, indent=2))

print("\n" + "="*60)
print("Running Agent 2...")
print("="*60)

result = planner.plan_mission(test_data)

print("\nResult:")
print(json.dumps(result, indent=2))
