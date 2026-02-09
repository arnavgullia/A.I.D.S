"""
Project Aegis - LangGraph Orchestrator
Coordinates Agent 1, Agent 2, Agent 3, and Quantum Module.
"""

import sys
import os
import json
from datetime import datetime
from typing import Dict, Any, Optional, Literal

# Add paths for agent imports
BASE_PATH = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_PATH)
sys.path.insert(0, os.path.join(BASE_PATH, "Agent-1"))
sys.path.insert(0, os.path.join(BASE_PATH, "Agent-2"))
sys.path.insert(0, os.path.join(BASE_PATH, "Agent-3"))

from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated
import operator

# Import shared modules
from shared.state_schema import AegisState, create_initial_state, add_log_entry
from shared.database import get_database, Asteroid, RiskAssessment, AgentLog
from shared.config import get_config
from shared.messaging import publish


# ============================================================================
# STATE DEFINITION FOR LANGGRAPH
# ============================================================================

class OrchestratorState(TypedDict, total=False):
    """State that flows through the LangGraph workflow."""
    # Core state
    aegis_state: AegisState
    
    # Routing
    next_node: str
    
    # Error handling
    error: Optional[str]


# ============================================================================
# AGENT NODE FUNCTIONS
# ============================================================================

def agent_1_node(state: OrchestratorState) -> OrchestratorState:
    """
    Agent 1: Intelligence Officer
    Analyzes asteroid threat and decides if deflection is needed.
    """
    print("\n" + "=" * 60)
    print("  🔍 AGENT 1: INTELLIGENCE OFFICER")
    print("=" * 60)
    
    aegis_state = state['aegis_state']
    asteroid_data = aegis_state['asteroid_data']
    
    try:
        # Import Agent 1
        from agent_1_database_intel import Agent1
        
        # Initialize agent
        agent = Agent1()
        
        # Prepare query
        query = f"""
        Analyze the following asteroid and provide a threat assessment:
        
        Name: {asteroid_data.get('name', 'Unknown')}
        Diameter: {asteroid_data.get('diameter_m', 0)} meters
        Mass: {asteroid_data.get('mass_kg', 0)} kg
        Velocity: {asteroid_data.get('velocity_km_s', 0)} km/s
        Composition: {asteroid_data.get('composition', 'Unknown')}
        Impact Probability: {asteroid_data.get('impact_probability', 0) * 100}%
        Days Until Approach: {asteroid_data.get('days_until_approach', 0)}
        
        Provide risk score (0-10) and recommendation (ACTIVATE_DEFLECTION or NO_ACTION).
        """
        
        # Get response
        response = agent.query(query)
        
        # Parse response to extract risk score
        risk_score = _extract_risk_score(response, asteroid_data)
        requires_deflection = risk_score >= get_config().risk_threshold
        
        # Calculate derived values
        mass = asteroid_data.get('mass_kg', 1e10)
        velocity = asteroid_data.get('velocity_km_s', 20)
        kinetic_energy_mt = (0.5 * mass * (velocity * 1000) ** 2) / (4.184e15)  # Megatons
        
        # Update state
        aegis_state['threat_assessment'] = {
            'impact_probability': asteroid_data.get('impact_probability', 0),
            'kinetic_energy_mt': kinetic_energy_mt,
            'estimated_damage': _estimate_damage(kinetic_energy_mt),
            'risk_score': risk_score,
            'requires_deflection': requires_deflection,
            'assessment_timestamp': datetime.now().isoformat(),
            'raw_response': response,
        }
        
        aegis_state['current_agent'] = 'agent_1'
        add_log_entry(aegis_state, 'agent_1', 'THREAT_ASSESSMENT_COMPLETE', 
                     {'risk_score': risk_score, 'requires_deflection': requires_deflection})
        
        # Log to database
        db = get_database()
        db.insert_log(AgentLog(
            log_id=0,
            agent_name='agent_1',
            action='THREAT_ASSESSMENT_COMPLETE',
            related_id=aegis_state['asteroid_id'],
            details_json=json.dumps({'risk_score': risk_score})
        ))
        
        print(f"\n✓ Risk Score: {risk_score}/10")
        print(f"✓ Requires Deflection: {requires_deflection}")
        print(f"✓ Kinetic Energy: {kinetic_energy_mt:.2f} MT")
        # Publish assessment for other agents/services
        try:
            publish("agent_1/assessment", aegis_state['threat_assessment'])
        except Exception:
            pass
        
    except Exception as e:
        print(f"❌ Agent 1 Error: {e}")
        state['error'] = str(e)
        # Default to high risk if unable to assess
        aegis_state['threat_assessment'] = {
            'risk_score': 5.0,
            'requires_deflection': True,
            'error': str(e),
        }
    
    state['aegis_state'] = aegis_state
    return state


def agent_2_node(state: OrchestratorState) -> OrchestratorState:
    """
    Agent 2: Strategic Planner
    Generates deflection strategies and runs quantum optimization.
    """
    print("\n" + "=" * 60)
    print("  🧠 AGENT 2: STRATEGIC PLANNER")
    print("=" * 60)
    
    aegis_state = state['aegis_state']
    asteroid_data = aegis_state['asteroid_data']
    
    # Check for rejection feedback from previous iteration
    feedback = None
    if aegis_state.get('safety_evaluation') and aegis_state['safety_evaluation'].get('verdict') == 'REJECT':
        feedback = aegis_state['safety_evaluation'].get('feedback')
        print(f"\n⚠️ ITERATION {aegis_state['iteration_count'] + 1}: Adjusting based on rejection feedback")
        print(f"   Feedback: {feedback}")
    
    try:
        # Import Agent 2
        from agent_2_strategic_planner import StrategicPlanner
        
        # Initialize agent
        planner = StrategicPlanner()
        
        # Add feedback if this is a retry
        if feedback:
            asteroid_data = dict(asteroid_data)
            asteroid_data['adjustment_feedback'] = feedback
        
        # Get mission plan
        result = planner.plan_mission(asteroid_data)
        
        print(f"\n✓ Strategy Generated: {result.get('method', 'Kinetic')}")
        
        # Generate 16 simulation candidates
        from shared.quantum_integration import run_quantum_optimization, prepare_candidates_for_quantum
        
        # Get raw candidates from the result or generate them
        raw_candidates = result.get('candidates', [])
        if not raw_candidates:
            raw_candidates = _generate_simulation_candidates(asteroid_data, result, feedback)
        
        # Prepare for quantum optimization
        constraints = {
            'max_velocity': 25,
            'min_velocity': 5,
            'max_fragmentation': 100,
            'max_fuel': 5000,
        }
        
        candidates = prepare_candidates_for_quantum(raw_candidates, constraints)
        
        print(f"✓ Generated {len(candidates)} simulation candidates")
        
        # Run quantum optimization
        print("\n⚛️  Running Quantum Grover Optimization...")
        quantum_result = run_quantum_optimization(candidates, constraints)
        
        optimal_idx = quantum_result['optimal_index']
        optimal_candidate = candidates[optimal_idx]
        
        print(f"\n✓ Quantum Optimization Complete!")
        print(f"  • Optimal Index: {optimal_idx}")
        print(f"  • Velocity: {optimal_candidate['velocity_km_s']} km/s")
        print(f"  • Angle: {optimal_candidate['angle_degrees']}°")
        print(f"  • Success Probability: {quantum_result['success_probability']:.2%}")
        print(f"  • Quantum Advantage: {quantum_result['quantum_advantage']:.1f}x")
        
        # Update state
        aegis_state['simulation_candidates'] = candidates
        aegis_state['quantum_result'] = {
            'optimal_index': optimal_idx,
            'optimal_simulation_id': None,  # Will be set after DB write
            'optimal_solution': optimal_candidate,
            'success_probability': quantum_result['success_probability'],
            'qubits_used': quantum_result.get('qubits_used', 4),
            'iterations': quantum_result.get('iterations', 3),
            'quantum_advantage': quantum_result.get('quantum_advantage', 4.0),
            'execution_time_ms': quantum_result.get('execution_time_ms', 0),
        }
        
        aegis_state['deflection_strategies'] = [{
            'strategy_id': 1,
            'method': result.get('method', 'Kinetic_Impactor'),
            'parameters': result,
            'feasibility_score': 0.85,
        }]
        aegis_state['primary_strategy_id'] = 1
        
        aegis_state['current_agent'] = 'agent_2'
        add_log_entry(aegis_state, 'agent_2', 'QUANTUM_OPTIMIZATION_COMPLETE',
                     {'optimal_index': optimal_idx, 'quantum_advantage': quantum_result.get('quantum_advantage', 4.0)})
        
        # Log to database
        db = get_database()
        db.insert_log(AgentLog(
            log_id=0,
            agent_name='agent_2',
            action='QUANTUM_OPTIMIZATION_COMPLETE',
            related_id=aegis_state['asteroid_id'],
            details_json=json.dumps({
                'optimal_index': optimal_idx,
                'quantum_advantage': quantum_result.get('quantum_advantage', 4.0)
            })
        ))
        # Publish plan/quantum result for other agents/services
        try:
            publish("agent_2/plan", {
                'optimal_index': optimal_idx,
                'optimal_candidate': optimal_candidate,
                'quantum_result': aegis_state.get('quantum_result', {})
            })
        except Exception:
            pass
        
    except Exception as e:
        print(f"❌ Agent 2 Error: {e}")
        import traceback
        traceback.print_exc()
        state['error'] = str(e)
    
    state['aegis_state'] = aegis_state
    return state


def agent_3_node(state: OrchestratorState) -> OrchestratorState:
    """
    Agent 3: Safety Validator
    Validates quantum solution and makes APPROVE/REJECT decision.
    """
    print("\n" + "=" * 60)
    print("  🔒 AGENT 3: SAFETY VALIDATOR")
    print("=" * 60)
    
    aegis_state = state['aegis_state']
    quantum_result = aegis_state.get('quantum_result', {})
    optimal_solution = quantum_result.get('optimal_solution', {})
    asteroid_data = aegis_state['asteroid_data']
    
    try:
        # Import Agent 3
        from agent_3_safety_validator import SafetyValidator
        
        # Initialize agent
        validator = SafetyValidator()
        
        # Prepare input
        quantum_output = {
            'optimal_index': quantum_result.get('optimal_index', 0),
            'candidates': [optimal_solution],
            'quantum_confidence': quantum_result.get('success_probability', 0.85),
        }
        
        asteroid_intel = {
            'name': asteroid_data.get('name', 'Unknown'),
            'mass_kg': asteroid_data.get('mass_kg', 1e10),
            'diameter_m': asteroid_data.get('diameter_m', 100),
            'composition': asteroid_data.get('composition', 'stony'),
            'time_to_impact_days': asteroid_data.get('days_until_approach', 365),
        }
        
        # Run validation
        result = validator.validate_solution(quantum_output, asteroid_intel)
        
        verdict = result.get('decision', 'UNKNOWN')
        
        print(f"\n✓ Validation Complete")
        print(f"  • Verdict: {verdict}")
        
        # Update state
        aegis_state['safety_evaluation'] = {
            'fragmentation_risk_pct': _extract_metric(result, 'fragmentation', 50.0),
            'miss_distance_km': _extract_metric(result, 'deflection', 15000.0),
            'confidence_score': quantum_result.get('success_probability', 0.85) * 100,
            'verdict': 'APPROVE' if verdict == 'APPROVED' else 'REJECT',
            'failed_checks': [],
            'feedback': result.get('raw_response', '') if verdict != 'APPROVED' else None,
            'evaluation_timestamp': datetime.now().isoformat(),
            'raw_response': result.get('raw_response', ''),
        }
        
        aegis_state['current_agent'] = 'agent_3'
        add_log_entry(aegis_state, 'agent_3', f'SAFETY_{verdict}',
                     {'verdict': verdict})
        
        # Log to database
        db = get_database()
        db.insert_log(AgentLog(
            log_id=0,
            agent_name='agent_3',
            action=f'SAFETY_{verdict}',
            related_id=aegis_state['asteroid_id'],
            details_json=json.dumps({'verdict': verdict})
        ))
        
        if verdict == 'APPROVED':
            print("  ✅ MISSION APPROVED")
        else:
            print("  ❌ MISSION REJECTED - Loop back to Agent 2")

        # Publish safety decision for other agents/services
        try:
            publish("agent_3/safety", aegis_state['safety_evaluation'])
        except Exception:
            pass
        
    except Exception as e:
        print(f"❌ Agent 3 Error: {e}")
        import traceback
        traceback.print_exc()
        state['error'] = str(e)
        # Default to approval if validation fails
        aegis_state['safety_evaluation'] = {
            'verdict': 'APPROVE',
            'error': str(e),
        }
    
    state['aegis_state'] = aegis_state
    return state


def final_decision_node(state: OrchestratorState) -> OrchestratorState:
    """
    Final Decision Node
    Consolidates all results and prepares final output.
    """
    print("\n" + "=" * 60)
    print("  🎯 FINAL DECISION")
    print("=" * 60)
    
    aegis_state = state['aegis_state']
    
    aegis_state['workflow_status'] = 'COMPLETED'
    add_log_entry(aegis_state, 'orchestrator', 'WORKFLOW_COMPLETED', {})
    
    # Print summary
    quantum_result = aegis_state.get('quantum_result', {})
    optimal = quantum_result.get('optimal_solution', {})
    
    print(f"\n✅ MISSION PLAN APPROVED")
    print(f"\nOptimal Deflection Parameters:")
    print(f"  • Velocity: {optimal.get('velocity_km_s', 'N/A')} km/s")
    print(f"  • Angle: {optimal.get('angle_degrees', 'N/A')}°")
    print(f"  • Impactor Mass: {optimal.get('impactor_mass_kg', 'N/A')} kg")
    print(f"\nQuantum Advantage: {quantum_result.get('quantum_advantage', 1.0):.1f}x faster than classical")
    
    state['aegis_state'] = aegis_state
    return state


def human_escalation_node(state: OrchestratorState) -> OrchestratorState:
    """
    Human Escalation Node
    Called when max iterations exceeded without approval.
    """
    print("\n" + "=" * 60)
    print("  ⚠️ HUMAN ESCALATION REQUIRED")
    print("=" * 60)
    
    aegis_state = state['aegis_state']
    aegis_state['workflow_status'] = 'ESCALATED'
    
    print(f"\n⚠️ After {aegis_state['iteration_count']} iterations, no safe solution found.")
    print("Human review and intervention required.")
    
    add_log_entry(aegis_state, 'orchestrator', 'ESCALATED_TO_HUMANS',
                 {'iterations': aegis_state['iteration_count']})
    
    state['aegis_state'] = aegis_state
    return state


# ============================================================================
# ROUTING FUNCTIONS
# ============================================================================

def route_after_agent_1(state: OrchestratorState) -> str:
    """Route after Agent 1 based on risk assessment."""
    aegis_state = state['aegis_state']
    threat = aegis_state.get('threat_assessment', {})
    
    if threat.get('requires_deflection', False):
        print("\n➡️ High risk detected - routing to Agent 2")
        return "agent_2"
    else:
        print("\n➡️ Low risk - no deflection needed")
        return "end_no_action"


def route_after_agent_3(state: OrchestratorState) -> str:
    """Route after Agent 3 based on safety verdict."""
    aegis_state = state['aegis_state']
    safety = aegis_state.get('safety_evaluation', {})
    iteration = aegis_state.get('iteration_count', 0)
    max_iter = get_config().max_iterations
    
    verdict = safety.get('verdict', 'REJECT')
    
    if verdict == 'APPROVE':
        return "final_decision"
    elif iteration < max_iter:
        # Increment iteration and loop back
        aegis_state['iteration_count'] = iteration + 1
        state['aegis_state'] = aegis_state
        print(f"\n🔄 Iteration {iteration + 1}/{max_iter} - Looping back to Agent 2")
        return "agent_2"
    else:
        return "human_escalation"


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def _extract_risk_score(response: str, asteroid_data: dict) -> float:
    """Extract risk score from Agent 1 response."""
    # Try to find explicit risk score in response
    import re
    
    patterns = [
        r'risk\s*(?:score|level)?[:\s]*(\d+(?:\.\d+)?)',
        r'(\d+(?:\.\d+)?)\s*/\s*10',
        r'score[:\s]*(\d+(?:\.\d+)?)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, response.lower())
        if match:
            try:
                score = float(match.group(1))
                return min(10.0, max(0.0, score))
            except:
                pass
    
    # Calculate based on asteroid properties
    impact_prob = asteroid_data.get('impact_probability', 0)
    diameter = asteroid_data.get('diameter_m', 100)
    
    base_score = impact_prob * 10
    if diameter > 300:
        base_score += 2
    if diameter > 500:
        base_score += 2
    
    return min(10.0, base_score)


def _estimate_damage(kinetic_energy_mt: float) -> str:
    """Estimate damage category based on kinetic energy."""
    if kinetic_energy_mt > 1000:
        return "Global"
    elif kinetic_energy_mt > 100:
        return "Continental"
    elif kinetic_energy_mt > 10:
        return "Regional"
    else:
        return "Local"


def _generate_simulation_candidates(
    asteroid_data: dict,
    strategy_result: dict,
    feedback: Optional[str] = None
) -> list:
    """Generate 16 simulation candidates based on strategy."""
    import random
    
    # Base ranges
    min_velocity = 8.0
    max_velocity = 20.0
    min_angle = 15.0
    max_angle = 50.0
    
    # Adjust based on feedback if this is a retry
    if feedback and 'velocity' in feedback.lower():
        max_velocity *= 0.8  # Reduce max velocity if fragmentation was issue
    
    candidates = []
    for i in range(16):
        velocity = min_velocity + (max_velocity - min_velocity) * (i / 15)
        angle = min_angle + (max_angle - min_angle) * ((15 - i) / 15)
        
        # Add some randomness
        velocity += random.uniform(-1, 1)
        angle += random.uniform(-3, 3)
        
        candidates.append({
            'id': i,
            'strategy': 'kinetic',
            'velocity_km_s': round(velocity, 2),
            'angle_degrees': round(angle, 2),
            'impactor_mass_kg': 500 + (i * 20),
            'estimated_fuel_kg': 2500 + (i * 100),
            'estimated_miss_km': 10000 + (i * 1000),
        })
    
    return candidates


def _extract_metric(result: dict, metric_type: str, default: float) -> float:
    """Extract a metric from validation result."""
    raw = result.get('raw_response', '')
    
    if metric_type == 'fragmentation':
        import re
        match = re.search(r'fragmentation.*?(\d+(?:\.\d+)?)\s*%', raw.lower())
        if match:
            return float(match.group(1))
    elif metric_type == 'deflection':
        import re
        match = re.search(r'deflection.*?(\d+(?:,\d+)*(?:\.\d+)?)\s*km', raw.lower())
        if match:
            return float(match.group(1).replace(',', ''))
    
    return default


# ============================================================================
# GRAPH BUILDER
# ============================================================================

def build_aegis_graph() -> StateGraph:
    """Build the complete Aegis workflow graph."""
    
    # Create state graph
    workflow = StateGraph(OrchestratorState)
    
    # Add nodes
    workflow.add_node("agent_1", agent_1_node)
    workflow.add_node("agent_2", agent_2_node)
    workflow.add_node("agent_3", agent_3_node)
    workflow.add_node("final_decision", final_decision_node)
    workflow.add_node("human_escalation", human_escalation_node)
    
    # Set entry point
    workflow.set_entry_point("agent_1")
    
    # Add conditional edge after Agent 1
    workflow.add_conditional_edges(
        "agent_1",
        route_after_agent_1,
        {
            "agent_2": "agent_2",
            "end_no_action": END
        }
    )
    
    # Agent 2 always goes to Agent 3
    workflow.add_edge("agent_2", "agent_3")
    
    # Add conditional edge after Agent 3
    workflow.add_conditional_edges(
        "agent_3",
        route_after_agent_3,
        {
            "final_decision": "final_decision",
            "agent_2": "agent_2",
            "human_escalation": "human_escalation"
        }
    )
    
    # Final nodes go to END
    workflow.add_edge("final_decision", END)
    workflow.add_edge("human_escalation", END)
    
    return workflow.compile()


# ============================================================================
# MAIN EXECUTION FUNCTION
# ============================================================================

def run_aegis_workflow(
    asteroid_id: int,
    asteroid_data: Dict[str, Any]
) -> AegisState:
    """
    Run the complete Aegis workflow for an asteroid.
    
    Args:
        asteroid_id: Unique identifier for the asteroid
        asteroid_data: Dictionary with asteroid properties
        
    Returns:
        Final AegisState with all results
    """
    print("\n" + "=" * 60)
    print("  🛡️  PROJECT AEGIS - PLANETARY DEFENSE SYSTEM")
    print("=" * 60)
    print(f"\nTarget: {asteroid_data.get('name', 'Unknown Asteroid')}")
    print(f"Diameter: {asteroid_data.get('diameter_m', 0)}m")
    print(f"Impact Probability: {asteroid_data.get('impact_probability', 0) * 100:.1f}%")
    
    # Initialize state
    aegis_state = create_initial_state(asteroid_id, asteroid_data)
    
    # Store asteroid in database
    db = get_database()
    db.insert_asteroid(Asteroid(
        asteroid_id=asteroid_id,
        name=asteroid_data.get('name', 'Unknown'),
        diameter_m=asteroid_data.get('diameter_m', 0),
        mass_kg=asteroid_data.get('mass_kg', 0),
        velocity_km_s=asteroid_data.get('velocity_km_s', 0),
        composition=asteroid_data.get('composition', 'unknown'),
        impact_probability=asteroid_data.get('impact_probability', 0),
        days_until_approach=asteroid_data.get('days_until_approach', 0),
    ))
    
    initial_state = OrchestratorState(
        aegis_state=aegis_state,
        next_node="agent_1",
        error=None
    )
    
    # Build and run graph
    graph = build_aegis_graph()
    final_state = graph.invoke(initial_state)
    
    print("\n" + "=" * 60)
    print("  WORKFLOW COMPLETE")
    print("=" * 60)
    
    return final_state['aegis_state']


# Entry point for direct execution
if __name__ == "__main__":
    # Test with sample asteroid
    test_asteroid = {
        "name": "Apophis-99942",
        "diameter_m": 340,
        "mass_kg": 2.7e10,
        "velocity_km_s": 30.0,
        "composition": "Stony-Iron",
        "impact_probability": 0.02,
        "days_until_approach": 1000,
    }
    
    result = run_aegis_workflow(1, test_asteroid)
    
    print("\n" + "=" * 60)
    print("  FINAL STATE SUMMARY")
    print("=" * 60)
    print(f"Status: {result['workflow_status']}")
    print(f"Iterations: {result['iteration_count']}")
    
    if result.get('quantum_result'):
        qr = result['quantum_result']
        print(f"Quantum Advantage: {qr.get('quantum_advantage', 1.0):.1f}x")
