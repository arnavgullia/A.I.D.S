"""
Main Entry Point for Agent 3: Safety Validator
"""

import sys
import os
import json
from dotenv import load_dotenv

# Ensure we can import local modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agent_3_safety_validator import SafetyValidator


def print_banner():
    """Print welcome banner."""
    print("\n" + "="*60)
    print("  🛡️  PROJECT AEGIS - PLANETARY DEFENSE SYSTEM")
    print("  🔒 Agent 3: Safety Validator")
    print("="*60)
    print("\nI am the FINAL GATEKEEPER. I validate quantum solutions and make")
    print("the GO/NO-GO decision for asteroid deflection missions.")
    print("\nType 'demo1' for an APPROVAL scenario")
    print("Type 'demo2' for a REJECTION scenario")
    print("Type 'custom' to input custom parameters")
    print("Type 'quit' or 'exit' to end the session.")
    print("-"*60 + "\n")


def get_demo_approval_data():
    """Get demo data that should result in APPROVAL."""
    return {
        "quantum_output": {
            "optimal_index": 7,
            "candidates": [
                {
                    "id": 7,
                    "velocity_km_s": 16.8,
                    "angle_deg": 18,
                    "impactor_mass_kg": 520
                }
            ],
            "quantum_confidence": 0.89
        },
        "asteroid_intel": {
            "name": "Apophis-99942",
            "mass_kg": 6.1e10,
            "diameter_m": 340,
            "composition": "stony",
            "time_to_impact_days": 1095
        }
    }


def get_demo_rejection_data():
    """Get demo data that should result in REJECTION (high fragmentation risk)."""
    return {
        "quantum_output": {
            "optimal_index": 14,
            "candidates": [
                {
                    "id": 14,
                    "velocity_km_s": 22.0,  # Too high - will cause fragmentation
                    "angle_deg": 35,
                    "impactor_mass_kg": 650
                }
            ],
            "quantum_confidence": 0.91
        },
        "asteroid_intel": {
            "name": "Apophis-99942",
            "mass_kg": 6.1e10,
            "diameter_m": 340,
            "composition": "stony",
            "time_to_impact_days": 1095
        }
    }


def get_custom_data():
    """Get custom parameters from user input."""
    print("\n[Custom Input Mode]")
    print("Enter asteroid and mission parameters:\n")
    
    try:
        name = input("Asteroid name [Apophis]: ").strip() or "Apophis"
        mass = float(input("Asteroid mass in kg [6.1e10]: ").strip() or "6.1e10")
        diameter = float(input("Asteroid diameter in meters [340]: ").strip() or "340")
        composition = input("Composition (stony/metallic/carbonaceous/icy/rubble) [stony]: ").strip() or "stony"
        time_days = int(input("Days until impact [1095]: ").strip() or "1095")
        
        print("\nMission parameters:")
        velocity = float(input("Impact velocity km/s [16.8]: ").strip() or "16.8")
        angle = float(input("Approach angle degrees [18]: ").strip() or "18")
        mass_impactor = float(input("Impactor mass kg [520]: ").strip() or "520")
        confidence = float(input("Quantum confidence 0-1 [0.89]: ").strip() or "0.89")
        
        return {
            "quantum_output": {
                "optimal_index": 0,
                "candidates": [{
                    "id": 0,
                    "velocity_km_s": velocity,
                    "angle_deg": angle,
                    "impactor_mass_kg": mass_impactor
                }],
                "quantum_confidence": confidence
            },
            "asteroid_intel": {
                "name": name,
                "mass_kg": mass,
                "diameter_m": diameter,
                "composition": composition,
                "time_to_impact_days": time_days
            }
        }
    except ValueError as e:
        print(f"❌ Invalid input: {e}")
        return None


def main():
    print_banner()
    
    # Check API Key
    load_dotenv()
    api_key = os.getenv("AGENT3_GOOGLE_API_KEY") or os.getenv("GOOGLE_API_KEY")
    
    if not api_key:
        print("\n[!] WARNING: No API Key found.")
        print("Please set AGENT3_GOOGLE_API_KEY or GOOGLE_API_KEY in .env file.")
        key = input("Or enter it here now: ").strip()
        if key:
            os.environ["GOOGLE_API_KEY"] = key
        else:
            print("Exiting.")
            return

    # Initialize Agent
    try:
        validator = SafetyValidator(model="gemini-2.5-flash-lite")
        print("✓ Safety Validator Initialized.\n")
    except Exception as e:
        print(f"❌ Failed to initialize Agent: {e}")
        return

    # Main loop
    while True:
        try:
            user_input = input("Command: ").strip().lower()
        except (KeyboardInterrupt, EOFError):
            print("\n\nGoodbye! Stay vigilant! 🚀")
            break
        
        if not user_input:
            continue
        
        if user_input in ["quit", "exit", "bye"]:
            print("\nGoodbye! Stay vigilant! 🚀")
            break
        
        # Get data based on command
        data = None
        
        if user_input == "demo1":
            print("\n[Demo 1: APPROVAL Scenario]")
            print("Testing with safe parameters (16.8 km/s velocity)...")
            data = get_demo_approval_data()
            
        elif user_input == "demo2":
            print("\n[Demo 2: REJECTION Scenario]")
            print("Testing with unsafe parameters (22.0 km/s velocity - fragmentation risk)...")
            data = get_demo_rejection_data()
            
        elif user_input == "custom":
            data = get_custom_data()
            
        else:
            print("Unknown command. Use 'demo1', 'demo2', 'custom', or 'quit'.")
            continue
        
        if data is None:
            continue
        
        # Display input
        print("\n" + "-"*40)
        print("📋 Input Data:")
        print("-"*40)
        print(json.dumps(data, indent=2))
        
        # Run validation
        print("\n" + "-"*40)
        print("🧠 Agent 3 is Validating...")
        print("-"*40)
        
        try:
            result = validator.validate_solution(
                data["quantum_output"],
                data["asteroid_intel"]
            )
            
            print("\n" + "="*60)
            print("  🔒 SAFETY VALIDATION RESULT")
            print("="*60)
            print(f"\nDECISION: {result['decision']}")
            print("\n" + "-"*40)
            print(result['raw_response'])
            print("="*60 + "\n")
            
        except Exception as e:
            print(f"\n❌ Validation Error: {e}\n")


if __name__ == "__main__":
    main()
