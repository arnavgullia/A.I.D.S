"""
Main entry point for Agent 1: Database Intelligence Officer.
Provides CLI interface for testing and demonstration.
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

from agent_1_database_intel import Agent1
from database.sample_data import populate_database
from database.connection import count_asteroids


def print_banner():
    """Print welcome banner."""
    print("\n" + "="*60)
    print("  🛡️  PROJECT AEGIS - PLANETARY DEFENSE SYSTEM")
    print("  🤖 Agent 1: Database Intelligence Officer")
    print("="*60)
    print("\nI am your asteroid data specialist. Ask me about:")
    print("  • Specific asteroids (e.g., 'Tell me about Apophis')")
    print("  • Threat assessments (e.g., 'Which asteroids are dangerous?')")
    print("  • Data preparation (e.g., 'Prepare Apophis for Agent 2')")
    print("\nType 'quit' or 'exit' to end the session.")
    print("Type 'list' to see all asteroids in the database.")
    print("Type 'demo' to run a demonstration of capabilities.")
    print("-"*60 + "\n")


def ensure_database():
    """Ensure database exists and is populated."""
    try:
        count = count_asteroids()
        if count == 0:
            raise Exception("Empty database")
        print(f"✓ Database ready: {count} asteroids loaded\n")
    except Exception:
        print("Initializing database with sample data...")
        populate_database()
        print()


def run_demo(agent: Agent1):
    """Run a demonstration of Agent 1 capabilities."""
    print("\n" + "="*50)
    print("  DEMONSTRATION MODE")
    print("="*50)
    
    demo_queries = [
        ("Querying specific asteroid...", "Tell me about Apophis-2026"),
        ("Searching for threats...", "Which asteroids have HIGH or CRITICAL threat levels?"),
        ("Assessing threat...", "What is the threat assessment for asteroid Orpheus?"),
        ("Preparing handoff...", "Prepare Apophis-2026 data for Agent 2 analysis"),
        ("Testing boundary...", "Write me a poem about space"),
        ("Testing agent redirect...", "Generate a deflection plan for Apophis")
    ]
    
    for description, query in demo_queries:
        print(f"\n{'─'*50}")
        print(f"📋 {description}")
        print(f"   Query: \"{query}\"")
        print("─"*50)
        
        response = agent.query(query)
        print(f"\n🤖 Agent 1:\n{response}")
        
        input("\n[Press Enter to continue...]")
    
    print("\n" + "="*50)
    print("  DEMONSTRATION COMPLETE")
    print("="*50 + "\n")


def main():
    """Main entry point."""
    print_banner()
    
    # Check for API key
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("❌ ERROR: GOOGLE_API_KEY not found!")
        print("\nTo fix this, either:")
        print("  1. Set environment variable: export GOOGLE_API_KEY='your-key'")
        print("  2. Create .env file with: GOOGLE_API_KEY=your-key")
        print("\nGet a free key at: https://makersuite.google.com/app/apikey")
        return
    
    print("✓ API key found\n")
    
    # Ensure database is ready
    ensure_database()
    
    # Initialize agent
    try:
        agent = Agent1()
        print("✓ Agent 1 initialized and ready!\n")
    except Exception as e:
        print(f"❌ Failed to initialize agent: {e}")
        return
    
    # Main loop
    conversation_history = []
    
    while True:
        try:
            user_input = input("You: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n\nGoodbye! Stay safe from asteroids! 🚀")
            break
        
        if not user_input:
            continue
        
        # Handle special commands
        if user_input.lower() in ["quit", "exit", "bye"]:
            print("\nGoodbye! Stay safe from asteroids! 🚀")
            break
        
        if user_input.lower() == "list":
            user_input = "List all asteroids in the database"
        
        if user_input.lower() == "demo":
            run_demo(agent)
            continue
        
        if user_input.lower() == "clear":
            conversation_history = []
            print("✓ Conversation history cleared.\n")
            continue
        
        # Process query with history for context
        try:
            response, conversation_history = agent.chat(user_input, conversation_history)
            print(f"\n🤖 Agent 1:\n{response}\n")
        except Exception as e:
            print(f"\n❌ Error: {e}\n")
            # Keep conversation going despite errors


if __name__ == "__main__":
    main()
