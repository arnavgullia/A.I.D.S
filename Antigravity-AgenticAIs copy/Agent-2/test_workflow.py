"""
Test Workflow: Agent 1 -> Agent 2 Integration
"""
import sys
import os
import json
from dotenv import load_dotenv
import subprocess

# Path setup
current_dir = os.path.dirname(os.path.abspath(__file__))
workspace_root = os.path.dirname(current_dir)
agent1_path = os.path.join(workspace_root, "Agent-1")
agent2_path = os.path.join(workspace_root, "Agent-2")

# We ONLY add Agent 2 to path to avoid 'tools' collision with Agent 1
sys.path.insert(0, agent2_path)

# Load env variables
load_dotenv(os.path.join(agent2_path, ".env")) 

from agent_2_strategic_planner import StrategicPlanner

def run_integration_test():
    print("="*60)
    print("🚀 PROJECT AEGIS: INTEGRATION TEST (AGENT 1 -> AGENT 2)")
    print("="*60)

    # 1. Get Data from Agent 1 (Running as Subprocess)
    # We create a temporary script in Agent 1's dir to output the data we want
    # This avoids import collisions
    print("\n[1] Querying Agent 1 (Subprocess)...")
    
    agent1_script = """
import sys
import os
import json
from dotenv import load_dotenv
sys.path.insert(0, os.getcwd())
load_dotenv()
from agent_1_database_intel import Agent1

def main():
    try:
        agent = Agent1()
        # We ask specifically for preparation to trigger the data formatter
        query = "Prepare Apophis-2026 data for Agent 2"
        response = agent.query(query)
        
        # Output ONLY the JSON block if possible, or the whole thing
        print(response)
    except Exception as e:
        print(json.dumps({"error": str(e)}))

if __name__ == "__main__":
    main()
"""
    
    script_path = os.path.join(agent1_path, "_temp_query.py")
    with open(script_path, "w") as f:
        f.write(agent1_script)
        
    try:
        result = subprocess.run(
            [sys.executable, "_temp_query.py"],
            cwd=agent1_path,
            capture_output=True,
            text=True
        )
        
        output = result.stdout.strip()
        # Cleanup
        if os.path.exists(script_path):
            os.remove(script_path)
            
        if result.returncode != 0:
            print(f"❌ Agent 1 Subprocess Failed: {result.stderr}")
            return

        print(f"✓ Agent 1 Responded ({len(output)} chars)")
        
        # Try to parse JSON from the output. Agent 1 output is usually markdown + text.
        # We look for the JSON block.
        import re
        # Look for JSON code block matching: ```json { ... } ```
        json_match = re.search(r'```json\s*(\{.*?\})\s*```', output, re.DOTALL)
        if not json_match:
             # Try just finding the first curly brace closure
             json_match = re.search(r'(\{.*\})', output, re.DOTALL)
             
        if json_match:
            json_str = json_match.group(1)
            try:
                data = json.loads(json_str)
                print("✓ Successfully extracted JSON from Agent 1 response")
            except json.JSONDecodeError:
                print("❌ Failed to parse extracted JSON.")
                print(f"Extracted string: {json_str[:200]}...")
                return
        else:
            print("❌ Could not find JSON in Agent 1 output.")
            print(f"Output excerpt: {output[:200]}...")
            return
            
    except Exception as e:
        print(f"❌ Subprocess Execution Failed: {e}")
        return

    # 3. Initialize Agent 2
    print("\n[3] Initializing Agent 2 (Strategic Planner)...")
    try:
        planner = StrategicPlanner(model="gemini-2.0-flash")
        print("✓ Agent 2 Ready")
    except Exception as e:
        print(f"❌ Failed to init Agent 2: {e}")
        return

    # 4. Pass Data to Agent 2
    print("\n[4] Handoff: Agent 1 Data -> Agent 2")
    try:
        plan = planner.plan_mission(data)
        print("✓ Agent 2 Generated Plan")
    except Exception as e:
        print(f"❌ Agent 2 Failed to process data: {e}")
        return

    # 5. Validation
    print("\n[5] Validating Final Output...")
    print(json.dumps(plan, indent=2))
    
    if plan.get("status") == "READY_FOR_QUANTUM":
        print("\n✅ SUCCESS: Full Workflow Verified!")
    else:
        print("\n❌ FAILURE: Invalid Final Status")
        print(f"Status: {plan.get('status')}")

if __name__ == "__main__":
    run_integration_test()
