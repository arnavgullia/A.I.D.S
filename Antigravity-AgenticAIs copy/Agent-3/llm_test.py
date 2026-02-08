"""LLM Test for Agent 3 - Using Gemini 2.0 Flash Lite"""
import sys
import os
import json
sys.path.insert(0, '/home/pranjay/workspace/Antigravity-AgenticAIs/Agent-3')

from dotenv import load_dotenv
load_dotenv('/home/pranjay/workspace/Antigravity-AgenticAIs/Agent-3/.env')

from agent_3_safety_validator import SafetyValidator

print("="*60)
print("  🔒 AGENT 3 LLM TEST - GEMINI 2.0 FLASH LITE")
print("="*60)

# Check API key
api_key = os.getenv("AGENT3_GOOGLE_API_KEY") or os.getenv("GOOGLE_API_KEY")
if not api_key:
    print("❌ No API key found!")
    sys.exit(1)
print("✓ API key found\n")

# Initialize with gemini-2.0-flash-lite
print("Initializing Agent 3 with gemini-2.0-flash-lite...")
try:
    validator = SafetyValidator(model="gemini-2.0-flash-lite")
    print("✓ Agent initialized!\n")
except Exception as e:
    print(f"❌ Failed to initialize: {e}")
    sys.exit(1)

# Test data - Safe scenario (should APPROVE)
print("-"*60)
print("TEST: Safe Parameters (expect APPROVE)")
print("-"*60)

quantum_output = {
    "optimal_index": 7,
    "candidates": [{
        "id": 7,
        "velocity_km_s": 16.8,
        "angle_deg": 18,
        "impactor_mass_kg": 520
    }],
    "quantum_confidence": 0.89
}

asteroid_intel = {
    "name": "Apophis-99942",
    "mass_kg": 6.1e10,
    "diameter_m": 340,
    "composition": "stony",
    "time_to_impact_days": 1095
}

print("Input:")
print(f"  Asteroid: {asteroid_intel['name']}")
print(f"  Velocity: {quantum_output['candidates'][0]['velocity_km_s']} km/s")
print(f"  Mass: {asteroid_intel['mass_kg']:.2e} kg")
print(f"  Confidence: {quantum_output['quantum_confidence']*100}%")
print()

print("🧠 Running validation...")
try:
    result = validator.validate_solution(quantum_output, asteroid_intel)
    
    print("\n" + "="*60)
    print(f"  DECISION: {result['decision']}")
    print("="*60)
    print("\nAgent Response:")
    print(result['raw_response'][:2000] if result['raw_response'] else "No response")
    
except Exception as e:
    print(f"❌ Error: {e}")
