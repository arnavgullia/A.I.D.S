#!/usr/bin/env python3
"""
Project Aegis - Main Entry Point
Run the complete multi-agent planetary defense system.

Usage:
    python run_aegis.py demo1       # Run with Apophis (high risk)
    python run_aegis.py demo2       # Run with small asteroid (low risk)
    python run_aegis.py custom      # Enter custom asteroid data
"""

import sys
import os
import json
import argparse
from datetime import datetime

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()


def print_banner():
    """Print the Aegis banner."""
    banner = """
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║     🛡️  PROJECT AEGIS - PLANETARY DEFENSE SYSTEM  🛡️         ║
║                                                              ║
║     Multi-Agent AI + Quantum Optimization                    ║
║                                                              ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  Agent 1: Intelligence Officer     → Threat Assessment      ║
║  Agent 2: Strategic Planner        → Deflection Strategy    ║
║  Quantum: Grover's Algorithm       → Optimal Solution       ║
║  Agent 3: Safety Validator         → Mission Approval       ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
"""
    print(banner)


def get_demo_asteroids():
    """Get predefined demo asteroids."""
    return {
        "demo1": {
            "name": "Apophis-99942",
            "diameter_m": 340,
            "mass_kg": 2.7e10,
            "velocity_km_s": 30.0,
            "composition": "Stony-Iron",
            "impact_probability": 0.02,  # 2% - HIGH
            "days_until_approach": 1000,
            "description": "High-risk asteroid requiring urgent deflection"
        },
        "demo2": {
            "name": "Small-Rock-001",
            "diameter_m": 30,
            "mass_kg": 1e7,
            "velocity_km_s": 15.0,
            "composition": "Stony",
            "impact_probability": 0.001,  # 0.1% - LOW
            "days_until_approach": 3650,
            "description": "Low-risk asteroid, likely no deflection needed"
        },
        "demo3": {
            "name": "Bennu-101955",
            "diameter_m": 500,
            "mass_kg": 7.3e10,
            "velocity_km_s": 28.0,
            "composition": "Rubble Pile",
            "impact_probability": 0.05,  # 5% - CRITICAL
            "days_until_approach": 36500,  # 100 years
            "description": "High-threat rubble pile with fragmentation risk"
        }
    }


def get_custom_asteroid():
    """Get custom asteroid data from user input."""
    print("\n[Custom Asteroid Input]")
    print("-" * 40)
    
    try:
        name = input("Asteroid name [CustomAsteroid]: ").strip() or "CustomAsteroid"
        diameter = float(input("Diameter in meters [100]: ").strip() or "100")
        mass = float(input("Mass in kg [1e10]: ").strip() or "1e10")
        velocity = float(input("Velocity in km/s [20]: ").strip() or "20")
        composition = input("Composition (stony/metallic/rubble/icy) [stony]: ").strip() or "stony"
        impact_prob = float(input("Impact probability 0-1 [0.01]: ").strip() or "0.01")
        days = int(input("Days until approach [365]: ").strip() or "365")
        
        return {
            "name": name,
            "diameter_m": diameter,
            "mass_kg": mass,
            "velocity_km_s": velocity,
            "composition": composition,
            "impact_probability": impact_prob,
            "days_until_approach": days
        }
    except ValueError as e:
        print(f"❌ Invalid input: {e}")
        return None


def check_api_keys():
    """Check if API keys are configured."""
    key = os.getenv("GOOGLE_API_KEY") or os.getenv("AGENT1_GOOGLE_API_KEY")
    if not key:
        print("❌ ERROR: No API key found!")
        print("\nPlease set one of the following environment variables:")
        print("  - GOOGLE_API_KEY")
        print("  - AGENT1_GOOGLE_API_KEY")
        print("\nOr create a .env file in the project root with:")
        print("  GOOGLE_API_KEY=your-api-key-here")
        return False
    print("✓ API key found")
    return True


def display_results(result):
    """Display the workflow results."""
    print("\n" + "=" * 60)
    print("  📊 EXECUTION SUMMARY")
    print("=" * 60)
    
    # Workflow status
    status = result.get('workflow_status', 'UNKNOWN')
    status_emoji = "✅" if status == "COMPLETED" else "⚠️" if status == "ESCALATED" else "❓"
    print(f"\n{status_emoji} Workflow Status: {status}")
    print(f"   Iterations: {result.get('iteration_count', 0)}")
    
    # Threat Assessment
    threat = result.get('threat_assessment', {})
    if threat:
        print(f"\n📋 Threat Assessment:")
        print(f"   Risk Score: {threat.get('risk_score', 'N/A')}/10")
        print(f"   Kinetic Energy: {threat.get('kinetic_energy_mt', 'N/A'):.2f} MT")
        print(f"   Damage Category: {threat.get('estimated_damage', 'N/A')}")
        print(f"   Deflection Required: {threat.get('requires_deflection', 'N/A')}")
    
    # Quantum Results
    quantum = result.get('quantum_result', {})
    if quantum:
        optimal = quantum.get('optimal_solution', {})
        print(f"\n⚛️  Quantum Optimization:")
        print(f"   Optimal Index: {quantum.get('optimal_index', 'N/A')}")
        print(f"   Success Probability: {quantum.get('success_probability', 0):.2%}")
        print(f"   Quantum Advantage: {quantum.get('quantum_advantage', 1.0):.1f}x faster")
        print(f"   Qubits Used: {quantum.get('qubits_used', 'N/A')}")
        print(f"   Grover Iterations: {quantum.get('iterations', 'N/A')}")
        
        if optimal:
            print(f"\n🎯 Optimal Deflection Parameters:")
            print(f"   Velocity: {optimal.get('velocity_km_s', 'N/A')} km/s")
            print(f"   Angle: {optimal.get('angle_degrees', 'N/A')}°")
            print(f"   Impactor Mass: {optimal.get('impactor_mass_kg', 'N/A')} kg")
    
    # Safety Evaluation
    safety = result.get('safety_evaluation', {})
    if safety:
        verdict = safety.get('verdict', 'UNKNOWN')
        verdict_emoji = "✅" if verdict == "APPROVE" else "❌"
        print(f"\n🔒 Safety Evaluation:")
        print(f"   {verdict_emoji} Verdict: {verdict}")
        print(f"   Fragmentation Risk: {safety.get('fragmentation_risk_pct', 'N/A')}%")
        print(f"   Miss Distance: {safety.get('miss_distance_km', 'N/A'):,.0f} km")
        print(f"   Confidence: {safety.get('confidence_score', 'N/A'):.1f}%")
    
    # Execution Log
    log = result.get('execution_log', [])
    if log:
        print(f"\n📝 Execution Log ({len(log)} entries):")
        for entry in log[-5:]:  # Show last 5 entries
            print(f"   [{entry['agent']}] {entry['action']}")


def main():
    """Main entry point."""
    print_banner()
    
    parser = argparse.ArgumentParser(description="Project Aegis - Planetary Defense System")
    parser.add_argument(
        'mode',
        nargs='?',
        default='demo1',
        choices=['demo1', 'demo2', 'demo3', 'custom'],
        help='Run mode: demo1 (Apophis), demo2 (low risk), demo3 (Bennu), custom'
    )
    parser.add_argument(
        '--json',
        type=str,
        help='Path to JSON file with asteroid data'
    )
    
    args = parser.parse_args()
    
    # Check API keys
    if not check_api_keys():
        return 1
    
    # Get asteroid data
    if args.json:
        try:
            with open(args.json, 'r') as f:
                asteroid_data = json.load(f)
            print(f"✓ Loaded asteroid data from {args.json}")
        except Exception as e:
            print(f"❌ Failed to load JSON: {e}")
            return 1
    elif args.mode == 'custom':
        asteroid_data = get_custom_asteroid()
        if not asteroid_data:
            return 1
    else:
        demos = get_demo_asteroids()
        asteroid_data = demos.get(args.mode, demos['demo1'])
        print(f"✓ Using demo asteroid: {asteroid_data['name']}")
        if 'description' in asteroid_data:
            print(f"  {asteroid_data['description']}")
    
    # Display asteroid info
    print("\n" + "-" * 40)
    print("📡 TARGET ASTEROID:")
    print("-" * 40)
    print(f"   Name: {asteroid_data.get('name', 'Unknown')}")
    print(f"   Diameter: {asteroid_data.get('diameter_m', 0):,.0f} m")
    print(f"   Mass: {asteroid_data.get('mass_kg', 0):.2e} kg")
    print(f"   Velocity: {asteroid_data.get('velocity_km_s', 0)} km/s")
    print(f"   Composition: {asteroid_data.get('composition', 'Unknown')}")
    print(f"   Impact Probability: {asteroid_data.get('impact_probability', 0) * 100:.1f}%")
    print(f"   Time to Impact: {asteroid_data.get('days_until_approach', 0)} days")
    print("-" * 40)
    
    # Confirm
    input("\nPress Enter to start the Aegis workflow...")
    
    # Run workflow
    try:
        from orchestrator import run_aegis_workflow
        
        # Generate unique asteroid ID
        asteroid_id = int(datetime.now().timestamp())
        
        result = run_aegis_workflow(asteroid_id, asteroid_data)
        
        # Display results
        display_results(result)
        
        # Export results
        output_file = f"aegis_result_{asteroid_data.get('name', 'unknown').replace(' ', '_')}.json"
        with open(output_file, 'w') as f:
            json.dump(result, f, indent=2, default=str)
        print(f"\n💾 Results saved to: {output_file}")
        
        return 0 if result.get('workflow_status') == 'COMPLETED' else 1
        
    except Exception as e:
        print(f"\n❌ Workflow Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
