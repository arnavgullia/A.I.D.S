
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
