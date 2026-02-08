"""
Test Workflow: Agent 2 -> Agent 3 Integration
Tests the handoff from Strategic Planner to Safety Validator.
"""
import sys
import os
import json
from dotenv import load_dotenv

# Path setup
current_dir = os.path.dirname(os.path.abspath(__file__))
workspace_root = os.path.dirname(current_dir)
agent3_path = current_dir

# Add Agent 3 to path
sys.path.insert(0, agent3_path)

# Load env variables
load_dotenv(os.path.join(agent3_path, ".env"))

from agent_3_safety_validator import SafetyValidator


def test_approval_scenario():
    """Test a scenario that should result in APPROVAL."""
    print("\n" + "="*60)
    print("TEST 1: APPROVAL SCENARIO")
    print("="*60)
    
    # Simulated output from Agent 2 + Quantum
    quantum_output = {
        "optimal_index": 7,
        "candidates": [
            {
                "id": 7,
                "velocity_km_s": 16.8,
                "angle_deg": 18,
                "impactor_mass_kg": 520
            }
        ],
        "quantum_confidence": 0.89,
        "strategy": "kinetic"
    }
    
    # Simulated data from Agent 1
    asteroid_intel = {
        "name": "Apophis-99942",
        "mass_kg": 6.1e10,
        "diameter_m": 340,
        "composition": "stony",
        "time_to_impact_days": 1095,
        "velocity_km_s": 30.73,
        "impact_probability": 0.92
    }
    
    print("\n📋 Quantum Output:")
    print(json.dumps(quantum_output, indent=2))
    print("\n📋 Asteroid Intel:")
    print(json.dumps(asteroid_intel, indent=2))
    
    print("\n🧠 Running Agent 3 Validation...")
    print("-"*40)
    
    try:
        validator = SafetyValidator(model="gemini-2.0-flash")
        result = validator.validate_solution(quantum_output, asteroid_intel)
        
        print("\n📊 Result:")
        print(f"Decision: {result['decision']}")
        print("\n" + result['raw_response'][:1000] + "...")
        
        if result['decision'] == "APPROVED":
            print("\n✅ TEST 1 PASSED: Solution correctly APPROVED")
            return True
        else:
            print("\n❌ TEST 1 FAILED: Expected APPROVED")
            return False
            
    except Exception as e:
        print(f"\n❌ TEST 1 ERROR: {e}")
        return False


def test_rejection_scenario():
    """Test a scenario that should result in REJECTION."""
    print("\n" + "="*60)
    print("TEST 2: REJECTION SCENARIO (High Fragmentation Risk)")
    print("="*60)
    
    # Dangerous parameters - velocity too high
    quantum_output = {
        "optimal_index": 14,
        "candidates": [
            {
                "id": 14,
                "velocity_km_s": 22.0,  # Too high - will fragment
                "angle_deg": 35,
                "impactor_mass_kg": 650
            }
        ],
        "quantum_confidence": 0.91,
        "strategy": "kinetic"
    }
    
    asteroid_intel = {
        "name": "Apophis-99942",
        "mass_kg": 6.1e10,
        "diameter_m": 340,
        "composition": "stony",
        "time_to_impact_days": 1095,
        "velocity_km_s": 30.73,
        "impact_probability": 0.92
    }
    
    print("\n📋 Quantum Output (DANGEROUS - 22 km/s):")
    print(json.dumps(quantum_output, indent=2))
    
    print("\n🧠 Running Agent 3 Validation...")
    print("-"*40)
    
    try:
        validator = SafetyValidator(model="gemini-2.0-flash")
        result = validator.validate_solution(quantum_output, asteroid_intel)
        
        print("\n📊 Result:")
        print(f"Decision: {result['decision']}")
        print("\n" + result['raw_response'][:1000] + "...")
        
        if result['decision'] == "REJECTED":
            print("\n✅ TEST 2 PASSED: Unsafe solution correctly REJECTED")
            return True
        else:
            print("\n❌ TEST 2 FAILED: Expected REJECTED (fragmentation risk)")
            return False
            
    except Exception as e:
        print(f"\n❌ TEST 2 ERROR: {e}")
        return False


def test_tool_calculation():
    """Test that the safety tools calculate correctly (without LLM)."""
    print("\n" + "="*60)
    print("TEST 3: TOOL CALCULATION VERIFICATION")
    print("="*60)
    
    from tools.safety_tools import (
        calculate_fragmentation_risk,
        calculate_deflection_distance,
        evaluate_safety_score
    )
    
    print("\n🔧 Testing fragmentation_risk tool...")
    frag_result = calculate_fragmentation_risk.invoke({
        "velocity_km_s": 16.8,
        "impactor_mass_kg": 520,
        "asteroid_mass_kg": 6.1e10,
        "asteroid_diameter_m": 340,
        "composition": "stony"
    })
    print(f"Result: {frag_result['fragmentation_risk_pct']}% - {frag_result['assessment']}")
    
    print("\n🔧 Testing deflection_distance tool...")
    defl_result = calculate_deflection_distance.invoke({
        "velocity_km_s": 16.8,
        "impactor_mass_kg": 520,
        "asteroid_mass_kg": 6.1e10,
        "time_to_impact_days": 1095
    })
    print(f"Result: {defl_result['deflection_distance_km']:,.0f} km - {defl_result['assessment']}")
    
    print("\n🔧 Testing safety_score tool...")
    score_result = evaluate_safety_score.invoke({
        "fragmentation_risk_pct": frag_result['fragmentation_risk_pct'],
        "deflection_distance_km": defl_result['deflection_distance_km'],
        "quantum_confidence": 0.89
    })
    print(f"Result: {score_result['recommendation']} (Score: {score_result['safety_score']})")
    
    # Verify values are reasonable
    checks = [
        frag_result['fragmentation_risk_pct'] < 100,
        defl_result['deflection_distance_km'] > 10000,
        score_result['recommendation'] == "APPROVE"
    ]
    
    if all(checks):
        print("\n✅ TEST 3 PASSED: All tool calculations verified")
        return True
    else:
        print("\n❌ TEST 3 FAILED: Tool calculations incorrect")
        return False


def run_integration_test():
    """Run all integration tests."""
    print("="*60)
    print("🚀 PROJECT AEGIS: AGENT 3 INTEGRATION TEST")
    print("="*60)
    
    # Check API key
    api_key = os.getenv("AGENT3_GOOGLE_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("\n❌ ERROR: No API key found!")
        print("Set AGENT3_GOOGLE_API_KEY or GOOGLE_API_KEY environment variable.")
        return
    
    print("✓ API key found")
    
    results = []
    
    # Test 3 first (no LLM required)
    results.append(("Tool Calculations", test_tool_calculation()))
    
    # Test 1: Approval scenario
    results.append(("Approval Scenario", test_approval_scenario()))
    
    # Test 2: Rejection scenario  
    results.append(("Rejection Scenario", test_rejection_scenario()))
    
    # Summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    
    passed = 0
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status}: {name}")
        if result:
            passed += 1
    
    print(f"\nTotal: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("\n🎉 ALL TESTS PASSED!")
    else:
        print("\n⚠️ Some tests failed. Check output above.")


if __name__ == "__main__":
    run_integration_test()
