"""
Project Aegis - Shared State Schema
Defines the state object that flows between all agents in the LangGraph workflow.
"""

from typing import TypedDict, Optional, List, Dict, Any, Annotated
from datetime import datetime
import operator


class ThreatAssessment(TypedDict, total=False):
    """Output from Agent 1: Intelligence Officer."""
    impact_probability: float  # 0.0 to 1.0
    kinetic_energy_mt: float  # Megatons TNT equivalent
    estimated_damage: str  # "Regional", "Continental", "Global"
    risk_score: float  # 0.0 to 10.0
    requires_deflection: bool
    assessment_timestamp: str
    raw_response: Optional[str]


class SimulationCandidate(TypedDict, total=False):
    """Single simulation candidate for quantum optimization."""
    candidate_id: int  # 0-15 for 4 qubits
    simulation_id: Optional[int]  # Database ID if stored
    strategy: str  # "kinetic", "gravity", etc.
    velocity_km_s: float
    angle_degrees: float
    timing_days: int
    impactor_mass_kg: float
    estimated_fuel_kg: float
    estimated_miss_km: float
    feasibility_score: float
    validity: bool  # For quantum oracle


class DeflectionStrategy(TypedDict, total=False):
    """Deflection strategy from Agent 2."""
    strategy_id: int
    method: str  # "Kinetic_Impactor", "Gravity_Tractor", "Nuclear"
    parameters: Dict[str, Any]
    feasibility_score: float


class QuantumResult(TypedDict, total=False):
    """Output from Quantum Grover optimization."""
    optimal_index: int  # 0-15
    optimal_simulation_id: Optional[int]
    optimal_solution: Dict[str, Any]  # The winning candidate's parameters
    success_probability: float
    qubits_used: int
    iterations: int
    quantum_advantage: float  # Speedup factor vs classical
    execution_time_ms: float


class SafetyEvaluation(TypedDict, total=False):
    """Output from Agent 3: Safety Validator."""
    fragmentation_risk_pct: float
    miss_distance_km: float
    confidence_score: float
    verdict: str  # "APPROVE" or "REJECT"
    failed_checks: List[str]
    feedback: Optional[str]  # Detailed feedback if rejected
    evaluation_timestamp: str
    raw_response: Optional[str]


class ExecutionLogEntry(TypedDict):
    """Single entry in the execution log."""
    timestamp: str
    agent: str
    action: str
    details: Dict[str, Any]


class AegisState(TypedDict, total=False):
    """
    Complete shared state for the Aegis workflow.
    This state flows through all agents via LangGraph.
    """
    # ========== INPUT DATA ==========
    asteroid_id: int
    asteroid_data: Dict[str, Any]  # Raw asteroid properties
    
    # ========== AGENT 1 OUTPUT ==========
    threat_assessment: Optional[ThreatAssessment]
    
    # ========== AGENT 2 OUTPUT ==========
    deflection_strategies: Optional[List[DeflectionStrategy]]
    primary_strategy_id: Optional[int]
    simulation_candidates: Optional[List[SimulationCandidate]]
    quantum_result: Optional[QuantumResult]
    
    # ========== AGENT 3 OUTPUT ==========
    safety_evaluation: Optional[SafetyEvaluation]
    
    # ========== CONTROL FLOW ==========
    iteration_count: int  # For rejection loop tracking
    current_agent: Optional[str]  # Current executing agent
    next_node: Optional[str]  # Routing instruction
    workflow_status: str  # "IN_PROGRESS", "COMPLETED", "ESCALATED"
    
    # ========== LOGGING ==========
    execution_log: List[ExecutionLogEntry]
    
    # ========== DATABASE IDs (populated after DB writes) ==========
    db_risk_assessment_id: Optional[int]
    db_strategy_ids: Optional[List[int]]
    db_simulation_ids: Optional[List[int]]
    db_quantum_result_id: Optional[int]
    db_safety_evaluation_id: Optional[int]
    db_final_decision_id: Optional[int]


def create_initial_state(
    asteroid_id: int,
    asteroid_data: Dict[str, Any]
) -> AegisState:
    """
    Create the initial state for a new Aegis workflow.
    
    Args:
        asteroid_id: Unique identifier for the asteroid
        asteroid_data: Dictionary containing asteroid properties:
            - name: str
            - diameter_m: float
            - mass_kg: float  
            - velocity_km_s: float
            - composition: str
            - impact_probability: float
            - days_until_approach: int
            
    Returns:
        Initialized AegisState ready for workflow execution
    """
    return AegisState(
        # Input
        asteroid_id=asteroid_id,
        asteroid_data=asteroid_data,
        
        # Agent outputs (will be populated during execution)
        threat_assessment=None,
        deflection_strategies=None,
        primary_strategy_id=None,
        simulation_candidates=None,
        quantum_result=None,
        safety_evaluation=None,
        
        # Control flow
        iteration_count=0,
        current_agent=None,
        next_node="agent_1",
        workflow_status="IN_PROGRESS",
        
        # Logging
        execution_log=[],
        
        # Database IDs
        db_risk_assessment_id=None,
        db_strategy_ids=None,
        db_simulation_ids=None,
        db_quantum_result_id=None,
        db_safety_evaluation_id=None,
        db_final_decision_id=None,
    )


def add_log_entry(
    state: AegisState,
    agent: str,
    action: str,
    details: Dict[str, Any] = None
) -> None:
    """
    Add an entry to the execution log.
    
    Args:
        state: Current workflow state
        agent: Name of the agent logging the entry
        action: Description of the action taken
        details: Optional additional details
    """
    entry = ExecutionLogEntry(
        timestamp=datetime.now().isoformat(),
        agent=agent,
        action=action,
        details=details or {}
    )
    
    if state.get("execution_log") is None:
        state["execution_log"] = []
    
    state["execution_log"].append(entry)
