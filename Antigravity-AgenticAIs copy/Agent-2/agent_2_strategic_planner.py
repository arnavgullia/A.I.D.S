"""
Agent 2: Strategic Planner
Core logic for Project Aegis's strategic planning component.
"""

import os
import json
from typing import Dict, Any, List, Union
from dotenv import load_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, BaseMessage
from langchain_core.tools import tool
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode

# Import local modules
from tools.simulation_generator import generate_simulation_space
from prompts.system_prompt import get_system_prompt

class StrategicPlanner:
    """
    Agent 2: Strategic Planner
    Responsible for analyzing asteroid data and defining the simulation search space.
    """

    def __init__(self, api_key: str = None, model: str = "gemini-2.5-flash-lite"):
        """
        Initialize the Strategic Planner.

        Args:
            api_key: Google API Key.
            model: Gemini model version.
        """
        # Load env if not provided
        if not api_key:
            load_dotenv()
            api_key = os.getenv("AGENT2_GOOGLE_API_KEY")
            # Fallback to standard key if specific agent key is missing
            if not api_key:
                 api_key = os.getenv("GOOGLE_API_KEY")
        
        if not api_key:
            raise ValueError("API Key not found. Please set AGENT2_GOOGLE_API_KEY or GOOGLE_API_KEY.")

        self.llm = ChatGoogleGenerativeAI(
            model=model,
            google_api_key=api_key,
            temperature=0.1 # Low temperature for precise reasoning
        )
        
        self.tools = [generate_simulation_space]
        self.llm_with_tools = self.llm.bind_tools(self.tools)
        self.system_prompt = get_system_prompt()
        self.graph = self._build_graph()

    def _build_graph(self):
        """Builds the LangGraph workflow."""
        from typing import TypedDict, Annotated, Sequence
        import operator

        class AgentState(TypedDict):
            messages: Annotated[Sequence[BaseMessage], operator.add]

        workflow = StateGraph(AgentState)

        # Node: Agent (LLM)
        def call_agent(state):
            messages = state['messages']
            # Ensure system prompt is first
            if not isinstance(messages[0], SystemMessage):
                messages = [SystemMessage(content=self.system_prompt)] + messages
            
            response = self.llm_with_tools.invoke(messages)
            return {"messages": [response]}

        # Node: Tools
        tool_node = ToolNode(self.tools)

        workflow.add_node("agent", call_agent)
        workflow.add_node("tools", tool_node)

        workflow.set_entry_point("agent")

        def should_continue(state):
            last_message = state['messages'][-1]
            if last_message.tool_calls:
                return "tools"
            return END

        workflow.add_conditional_edges("agent", should_continue)
        workflow.add_edge("tools", "agent")

        return workflow.compile()

    def plan_mission(self, asteroid_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main entry point for the agent.
        Takes asteroid data, runs the reasoning loop, and returns the final plan.
        """
        # Convert JSON structure to a readable string for the LLM
        # We want to format it clearly so the LLM understands the physics
        
        asteroid_str = json.dumps(asteroid_data, indent=2)
        user_message = f"Here is the data for the incoming asteroid. Analyze it and generate the simulation search space.\n\n{asteroid_str}"

        initial_state = {"messages": [SystemMessage(content=self.system_prompt), HumanMessage(content=user_message)]}
        
        # Run the graph
        # We need to capture the final output which should be the JSON summary
        final_response = None
        
        # Stream or invoke
        events = self.graph.stream(initial_state)
        
        for event in events:
            if "agent" in event:
                msg = event["agent"]["messages"][0]
                if not msg.tool_calls:
                    final_response = msg.content
        
        # Parse the final response to ensure it's valid JSON
        try:
             # Find the JSON block in the markdown if present
            content = final_response.strip()
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
                
            return json.loads(content)
        except Exception as e:
            return {
                "error": "Failed to parse Agent output",
                "raw_output": final_response,
                "details": str(e)
            }

if __name__ == "__main__":
    # Test
    agent = StrategicPlanner()
    test_data = {
        "name": "Test-Rock",
        "mass": 1e10,
        "diameter": 100,
        "impact_probability": 0.2,
        "time_to_impact": "2 years",
        "composition": "Iron"
    }
    # print(agent.plan_mission(test_data))
    pass
