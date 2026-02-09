"""
Agent 3: Safety Validator
Core logic for Project Aegis's safety validation component.
"""

import os
import json
from typing import Dict, Any, Sequence
from dotenv import load_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, BaseMessage
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode

# Import local modules
from tools.safety_tools import (
    calculate_fragmentation_risk,
    calculate_deflection_distance,
    evaluate_safety_score
)
from prompts.system_prompt import get_system_prompt
from shared.messaging import subscribe


class SafetyValidator:
    """
    Agent 3: Safety Validator
    Responsible for validating quantum-optimized deflection solutions.
    Has absolute veto power over mission approval.
    """

    def __init__(self, api_key: str = None, model: str = "gemini-2.0-flash"):
        """
        Initialize the Safety Validator.

        Args:
            api_key: Google API Key.
            model: Gemini model version.
        """
        # Load env if not provided
        if not api_key:
            load_dotenv()
            api_key = os.getenv("AGENT3_GOOGLE_API_KEY")
            # Fallback to standard key if specific agent key is missing
            if not api_key:
                api_key = os.getenv("GOOGLE_API_KEY")
        
        if not api_key:
            raise ValueError("API Key not found. Please set AGENT3_GOOGLE_API_KEY or GOOGLE_API_KEY.")

        self.llm = ChatGoogleGenerativeAI(
            model=model,
            google_api_key=api_key,
            temperature=0.1  # Low temperature for precise, consistent decisions
        )
        
        self.tools = [
            calculate_fragmentation_risk,
            calculate_deflection_distance,
            evaluate_safety_score
        ]
        self.llm_with_tools = self.llm.bind_tools(self.tools)
        self.system_prompt = get_system_prompt()
        self.graph = self._build_graph()
        # Subscribe to Agent 2 plan events to receive the chosen solution
        self.last_plan = None
        try:
            def _on_plan(topic, payload):
                self.last_plan = payload

            subscribe("agent_2/plan", _on_plan)
        except Exception:
            pass

    def _build_graph(self):
        """Builds the LangGraph workflow for agent-tool interaction."""
        from typing import TypedDict, Annotated
        import operator

        class AgentState(TypedDict):
            messages: Annotated[Sequence[BaseMessage], operator.add]

        workflow = StateGraph(AgentState)

        # Node: Agent (LLM)
        def call_agent(state):
            messages = state['messages']
            # Ensure system prompt is first
            if not isinstance(messages[0], SystemMessage):
                messages = [SystemMessage(content=self.system_prompt)] + list(messages)
            
            response = self.llm_with_tools.invoke(messages)
            return {"messages": [response]}

        # Node: Tools
        tool_node = ToolNode(self.tools)

        workflow.add_node("agent", call_agent)
        workflow.add_node("tools", tool_node)

        workflow.set_entry_point("agent")

        def should_continue(state):
            last_message = state['messages'][-1]
            if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
                return "tools"
            return END

        workflow.add_conditional_edges("agent", should_continue)
        workflow.add_edge("tools", "agent")

        return workflow.compile()

    def validate_solution(
        self, 
        quantum_output: Dict[str, Any], 
        asteroid_intel: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Main entry point for the agent.
        Takes quantum output and asteroid data, runs validation, and returns decision.
        
        Args:
            quantum_output: Output from quantum algorithm containing optimal candidate
            asteroid_intel: Asteroid data from Agent 1
            
        Returns:
            Validation result with APPROVE/REJECT decision and reasoning
        """
        # Build the input message for the agent
        input_data = {
            "quantum_output": quantum_output,
            "asteroid_intel": asteroid_intel
        }
        
        input_str = json.dumps(input_data, indent=2)
        user_message = f"""Here is the quantum-optimized deflection solution for validation.

Extract the optimal candidate parameters and validate using your safety tools.

{input_str}

Run all three safety checks and provide your final APPROVE or REJECT decision."""

        initial_state = {
            "messages": [
                SystemMessage(content=self.system_prompt), 
                HumanMessage(content=user_message)
            ]
        }
        
        # Run the graph
        final_response = None
        
        events = self.graph.stream(initial_state)
        
        for event in events:
            if "agent" in event:
                msg = event["agent"]["messages"][0]
                if not (hasattr(msg, 'tool_calls') and msg.tool_calls):
                    final_response = msg.content
        
        # Parse the response to determine decision
        decision = self._parse_decision(final_response)
        
        return {
            "decision": decision,
            "raw_response": final_response,
            "quantum_input": quantum_output,
            "asteroid_intel": asteroid_intel
        }

    def _parse_decision(self, response: str) -> str:
        """Parse the agent's response to extract the decision."""
        if response is None:
            return "ERROR"
        
        response_upper = response.upper()
        
        if "MISSION APPROVED" in response_upper or "✅ APPROVE" in response_upper:
            return "APPROVED"
        elif "MISSION REJECTED" in response_upper or "❌ REJECT" in response_upper:
            return "REJECTED"
        else:
            # Check for approval/rejection keywords
            if "APPROVE" in response_upper and "REJECT" not in response_upper:
                return "APPROVED"
            elif "REJECT" in response_upper:
                return "REJECTED"
            else:
                return "UNKNOWN"

    def quick_validate(
        self,
        velocity_km_s: float,
        impactor_mass_kg: float,
        angle_deg: float,
        asteroid_name: str,
        asteroid_mass_kg: float,
        asteroid_diameter_m: float,
        composition: str,
        time_to_impact_days: int,
        quantum_confidence: float
    ) -> Dict[str, Any]:
        """
        Convenience method for quick validation with explicit parameters.
        
        Args:
            velocity_km_s: Impact velocity
            impactor_mass_kg: Spacecraft mass
            angle_deg: Approach angle
            asteroid_name: Target name
            asteroid_mass_kg: Target mass
            asteroid_diameter_m: Target diameter
            composition: Material type
            time_to_impact_days: Days until Earth impact
            quantum_confidence: Optimization confidence (0-1)
            
        Returns:
            Validation result
        """
        quantum_output = {
            "optimal_index": 0,
            "candidates": [{
                "id": 0,
                "velocity_km_s": velocity_km_s,
                "angle_deg": angle_deg,
                "impactor_mass_kg": impactor_mass_kg
            }],
            "quantum_confidence": quantum_confidence
        }
        
        asteroid_intel = {
            "name": asteroid_name,
            "mass_kg": asteroid_mass_kg,
            "diameter_m": asteroid_diameter_m,
            "composition": composition,
            "time_to_impact_days": time_to_impact_days
        }
        
        return self.validate_solution(quantum_output, asteroid_intel)


if __name__ == "__main__":
    # Quick test
    agent = SafetyValidator()
    print("✓ Safety Validator initialized successfully")
