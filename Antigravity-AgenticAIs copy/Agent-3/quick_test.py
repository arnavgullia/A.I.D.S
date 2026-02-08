"""Quick test script for Agent 3 tools"""
import sys
sys.path.insert(0, '/home/pranjay/workspace/Antigravity-AgenticAIs/Agent-3')

from tools.safety_tools import calculate_fragmentation_risk, calculate_deflection_distance, evaluate_safety_score

print("="*50)
print("TEST: Safe Scenario (Should APPROVE)")
print("="*50)

frag = calculate_fragmentation_risk.invoke({
    "velocity_km_s": 16.8,
    "impactor_mass_kg": 520,
    "asteroid_mass_kg": 6.1e10,
    "asteroid_diameter_m": 340,
    "composition": "stony"
})

defl = calculate_deflection_distance.invoke({
    "velocity_km_s": 16.8,
    "impactor_mass_kg": 520,
    "asteroid_mass_kg": 6.1e10,
    "time_to_impact_days": 1095
})

score = evaluate_safety_score.invoke({
    "fragmentation_risk_pct": frag['fragmentation_risk_pct'],
    "deflection_distance_km": defl['deflection_distance_km'],
    "quantum_confidence": 0.89
})

print("\n" + "="*50)
print("SUMMARY")
print("="*50)
print(f"Fragmentation: {frag['fragmentation_risk_pct']}% ({frag['assessment']})")
print(f"Deflection: {defl['deflection_distance_km']:,.0f} km ({defl['assessment']})")
print(f"Decision: {score['recommendation']}")
print("="*50)
