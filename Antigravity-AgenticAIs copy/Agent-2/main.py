"""
Main Entry Point for Agent 2: Strategic Planner
"""

import sys
import os
import json
from dotenv import load_dotenv

# Ensure we can import local modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agent_2_strategic_planner import StrategicPlanner

def main():
    print("\n" + "="*60)
    print("  🛡️  PROJECT AEGIS - AGENT 2: STRATEGIC PLANNER")
    print("="*60)
    
    # Check API Key
    load_dotenv()
    if not os.getenv("AGENT2_GOOGLE_API_KEY") and not os.getenv("GOOGLE_API_KEY"):
         print("\n[!] WARNING: No API Key found.")
         print("Please set AGENT2_GOOGLE_API_KEY in the .env file.")
         key = input("Or enter it here now: ").strip()
         if key:
             os.environ["AGENT2_GOOGLE_API_KEY"] = key
         else:
             print("Exiting.")
             return

    # Initialize Agent
    try:
        planner = StrategicPlanner(model="gemini-2.5-flash-lite")
        print("✓ Strategic Planner Initialized.")
    except Exception as e:
        print(f"❌ Failed to initialize Agent: {e}")
        return

    print("\n[Input Mode] Enter Asteroid JSON Data.")
    print("You can paste a full JSON object. Typle 'END' on a new line when done.")
    print("Or type 'demo1' for Apophis (Kinetic) or 'demo2' for Bennu (Gravity).")
    
    buffer = []
    while True:
        line = input(">> ")
        if line.strip().upper() == 'END':
            break
        if line.strip().lower() == 'demo1':
            buffer = [json.dumps({
                "name": "Apophis-99942",
                "diameter_m": 340,
                "mass_kg": 2.7e10,
                "composition": "Stony-Iron",
                "impact_probability": 0.02, # 2% > 1%
                "days_until_approach": 1000, # < 5 years
                "velocity_km_s": 30.0
            })]
            print(f"Loaded Demo 1: Apophis (High Threat, Urgent)")
            break
        if line.strip().lower() == 'demo2':
            buffer = [json.dumps({
                "name": "Bennu-101955",
                "diameter_m": 500,
                "mass_kg": 7.3e10,
                "composition": "Rubble Pile",
                "impact_probability": 0.05, # 5% > 1%
                "days_until_approach": 36500, # 100 years > 5 years
                "velocity_km_s": 28.0
            })]
            print(f"Loaded Demo 2: Bennu (High Threat, Long Term)")
            break
            
        buffer.append(line)
        
    raw_input = "".join(buffer)
    
    try:
        data = json.loads(raw_input)
    except json.JSONDecodeError:
        print("❌ Invalid JSON input.")
        return

    print("\n" + "-"*40)
    print("🧠 Agent 2 is Thinking & Planning...")
    print("-"*40)
    
    result = planner.plan_mission(data)
    
    print("\n" + "="*60)
    print("  🚀 MISSION PLAN (HANDOFF FOR QUANTUM AGENT)")
    print("="*60)
    print(json.dumps(result, indent=2))
    print("\n[Done]")

if __name__ == "__main__":
    main()
