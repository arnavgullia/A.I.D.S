# Agent 1: Database Intelligence Officer

Project Aegis - AI-driven planetary defense decision system.

Agent 1 is the intelligent interface between the asteroid database and users/agents.

## Setup

1. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up Gemini API key:
```bash
export GOOGLE_API_KEY="your-api-key-here"
# Or create .env file with GOOGLE_API_KEY=your-key
```

4. Initialize database with sample data:
```bash
python -m database.sample_data
```

5. Run the agent:
```bash
python main.py
```

## Usage

Interactive CLI mode:
```bash
python main.py
```

Or programmatic:
```python
from agent_1_database_intel import Agent1

agent = Agent1()
response = agent.query("Tell me about Apophis-2026")
print(response)
```

## Capabilities

- Retrieve asteroid data from database
- Search/filter asteroids by criteria
- Basic threat assessments
- Data validation
- Format data for Agent 2/quantum system

## Domain Boundaries

**Handles:** Asteroids, NEOs, planetary defense, database queries

**Redirects to Agent 2:** Deflection strategies, mission planning

**Redirects to Agent 3:** Safety validation, mission approval
