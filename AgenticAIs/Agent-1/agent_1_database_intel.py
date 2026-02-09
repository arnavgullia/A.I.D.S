"""
Agent 1: Database Intelligence Officer
Main implementation using LangGraph and Google Gemini.

This agent serves as the intelligent interface between the asteroid database
and users/other agents in the Project Aegis planetary defense system.
"""

import os
import time
from typing import Annotated, TypedDict, Sequence
from dotenv import load_dotenv

from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage, AIMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode

# Load environment variables
load_dotenv()

# Import tools
from tools.database_query import database_query_tool, list_all_asteroids
from tools.database_search import database_search_tool
from tools.threat_calculator import threat_calculator_tool
from tools.data_formatter import data_formatter_tool
from tools.data_validator import data_validator_tool

# Import system prompt
from prompts.system_prompt import get_system_prompt


class AgentState(TypedDict):
    """State for the Agent 1 graph."""
    messages: Annotated[Sequence[BaseMessage], "The messages in the conversation"]


# Models to try in order of preference
GEMINI_MODELS = [
    "gemini-2.5-flash-lite",  # Best free tier availability
    "gemini-2.0-flash",
    "gemini-2.5-flash",
]

# Rate limit: minimum seconds between API requests
API_REQUEST_DELAY = 35


class Agent1:
    """
    Agent 1: Database Intelligence Officer
    
    The intelligent interface between the asteroid database and users.
    Uses Gemini LLM for reasoning and LangGraph for orchestration.
    """
    
    def __init__(self, api_key: str = None, model: str = None):
        """
        Initialize Agent 1.
        
        Args:
            api_key: Google API key. If not provided, looks for GOOGLE_API_KEY env var.
            model: Specific model to use. If not provided, uses default from GEMINI_MODELS.
        """
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        
        if not self.api_key:
            raise ValueError(
                "Google API key required. Set GOOGLE_API_KEY environment variable "
                "or pass api_key parameter."
            )
        
        # Use specified model or default
        self.model_name = model or GEMINI_MODELS[0]
        
        # Initialize Gemini LLM
        self.llm = ChatGoogleGenerativeAI(
            model=self.model_name,
            google_api_key=self.api_key,
            temperature=0.1,  # Low temperature for consistent, precise responses
            convert_system_message_to_human=True  # Gemini compatibility
        )
        
        # Define available tools
        self.tools = [
            database_query_tool,
            list_all_asteroids,
            database_search_tool,
            threat_calculator_tool,
            data_formatter_tool,
            data_validator_tool
        ]
        
        # Bind tools to LLM
        self.llm_with_tools = self.llm.bind_tools(self.tools)
        
        # System prompt
        self.system_prompt = get_system_prompt()
        
        # Build the agent graph
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph agent workflow."""
        
        # Create the graph
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("agent", self._call_agent)
        workflow.add_node("tools", ToolNode(self.tools))
        
        # Set entry point
        workflow.set_entry_point("agent")
        
        # Add conditional edges
        workflow.add_conditional_edges(
            "agent",
            self._should_continue,
            {
                "continue": "tools",
                "end": END
            }
        )
        
        # Tools always return to agent
        workflow.add_edge("tools", "agent")
        
        # Compile and return
        return workflow.compile()
    
    def _call_agent(self, state: AgentState) -> dict:
        """Call the agent (LLM) node with retry logic."""
        messages = list(state["messages"])
        
        # Ensure we have valid messages - system + at least one user message
        if not messages:
            messages = [HumanMessage(content="Hello")]
        
        # Add system message context if not present
        if not any(isinstance(m, SystemMessage) for m in messages):
            messages = [SystemMessage(content=self.system_prompt)] + messages
        
        # Retry logic for rate limits (35s minimum between requests)
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = self.llm_with_tools.invoke(messages)
                return {"messages": messages + [response]}
            except Exception as e:
                error_str = str(e)
                if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str:
                    wait_time = API_REQUEST_DELAY  # 35 seconds
                    print(f"Rate limited. Waiting {wait_time}s before retry {attempt + 1}/{max_retries}...")
                    time.sleep(wait_time)
                else:
                    raise
        
        raise Exception(f"Failed after {max_retries} retries due to rate limiting")
    
    def _should_continue(self, state: AgentState) -> str:
        """Determine if we should continue to tools or end."""
        last_message = state["messages"][-1]
        
        # If the LLM made tool calls, continue to tools
        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            return "continue"
        
        # Otherwise, end
        return "end"
    
    def query(self, user_input: str) -> str:
        """
        Process a user query and return the response.
        
        Args:
            user_input: The user's question or request
            
        Returns:
            The agent's response as a string
        """
        # Initialize state with user message
        initial_state = {
            "messages": [
                SystemMessage(content=self.system_prompt),
                HumanMessage(content=user_input)
            ]
        }
        
        # Run the graph
        result = self.graph.invoke(initial_state)
        
        # Extract the final response
        final_message = result["messages"][-1]
        
        if isinstance(final_message, AIMessage):
            return final_message.content
        
        return str(final_message)
    
    def chat(self, user_input: str, history: list = None) -> tuple[str, list]:
        """
        Process a query with conversation history.
        
        Args:
            user_input: The user's question or request
            history: Previous conversation messages
            
        Returns:
            Tuple of (response string, updated history)
        """
        # Build message history
        messages = [SystemMessage(content=self.system_prompt)]
        
        if history:
            messages.extend(history)
        
        messages.append(HumanMessage(content=user_input))
        
        # Run the graph
        result = self.graph.invoke({"messages": messages})
        
        # Extract response and update history
        final_message = result["messages"][-1]
        response = final_message.content if isinstance(final_message, AIMessage) else str(final_message)
        
        # Update history (excluding system message)
        new_history = result["messages"][1:]
        
        return response, new_history


def create_agent(api_key: str = None, model: str = None) -> Agent1:
    """
    Factory function to create Agent 1.
    
    Args:
        api_key: Optional Google API key
        model: Optional specific Gemini model to use
        
    Returns:
        Configured Agent1 instance
    """
    return Agent1(api_key=api_key, model=model)


# For testing
if __name__ == "__main__":
    # Quick test
    agent = Agent1()
    response = agent.query("Tell me about Apophis-2026")
    print(response)
