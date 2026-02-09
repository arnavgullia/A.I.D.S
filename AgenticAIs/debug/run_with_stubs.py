"""Debug runner: injects lightweight stubs for Agent-1/2/3 and runs the orchestrator.

This exercises the workflow end-to-end without any external LLM or network calls.
Run from the repository root with the project's virtualenv Python.
"""
import os
import sys
import json
import types
import traceback

# Ensure the parent Antigravity-AgenticAIs copy folder is on sys.path so
# imports like `orchestrator` resolve when this script is executed.
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

# Create simple stubs matching the expected agent classes/functions
mod1 = types.ModuleType("agent_1_database_intel")
class Agent1Stub:
    def query(self, q):
        # Return a deterministic high-risk response
        return "Risk score: 7/10\nRecommendation: ACTIVATE_DEFLECTION"
mod1.Agent1 = Agent1Stub
sys.modules["agent_1_database_intel"] = mod1

mod2 = types.ModuleType("agent_2_strategic_planner")
class StrategicPlannerStub:
    def plan_mission(self, data):
        # Provide 16 candidate dicts
        candidates = []
        for i in range(16):
            candidates.append({
                'id': i,
                'velocity_km_s': 8.0 + i * 0.8,
                'angle_degrees': 15.0 + i * 2.5,
                'impactor_mass_kg': 500 + i * 20,
                'estimated_fuel_kg': 2500 + i * 100,
                'score': 0.5 + (0.03 * i if i < 10 else -0.02 * i),
                'validity': i not in [3,10,14]
            })
        return {'method': 'kinetic', 'candidates': candidates}
mod2.StrategicPlanner = StrategicPlannerStub
sys.modules["agent_2_strategic_planner"] = mod2

mod3 = types.ModuleType("agent_3_safety_validator")
class SafetyValidatorStub:
    def validate_solution(self, quantum_output, asteroid_intel):
        # Approve simple expected solution
        return {'decision': 'APPROVED', 'raw_response': 'APPROVED by stub'}
mod3.SafetyValidator = SafetyValidatorStub
sys.modules["agent_3_safety_validator"] = mod3

def main():
    try:
        # Run a simplified local workflow that mirrors orchestrator logic,
        # but uses the stubbed agents above to avoid importing heavy deps.
        from shared.quantum_integration import prepare_candidates_for_quantum, run_quantum_optimization

        asteroid = {
            'name': 'Stub-Rock',
            'diameter_m': 200,
            'mass_kg': 5e9,
            'velocity_km_s': 22.0,
            'composition': 'stony',
            'impact_probability': 0.02,
            'days_until_approach': 800
        }

        print("[debug] Running simplified workflow with stubbed agents...")

        # Agent 1
        agent1 = mod1.Agent1()
        resp = agent1.query("Assess threat")
        # Simple extraction of risk score if present
        risk_score = 0.0
        try:
            import re
            m = re.search(r"(\d+(?:\.\d+)?)\s*/?\s*10", resp)
            if m:
                risk_score = float(m.group(1))
            else:
                m2 = re.search(r"(\d+(?:\.\d+)?)", resp)
                if m2:
                    risk_score = float(m2.group(1))
        except Exception:
            risk_score = 5.0

        requires_deflection = risk_score >= 4.0

        aegis_state = {
            'asteroid_id': 42,
            'asteroid_data': asteroid,
            'threat_assessment': {
                'risk_score': risk_score,
                'requires_deflection': requires_deflection
            }
        }

        if not requires_deflection:
            aegis_state['workflow_status'] = 'COMPLETED'
            print("[debug] Low risk - no action required")
            print(json.dumps(aegis_state, indent=2, default=str))
            return 0

        # Agent 2 - planning
        planner = mod2.StrategicPlanner()
        plan = planner.plan_mission(asteroid)
        raw_candidates = plan.get('candidates', [])
        constraints = {'max_velocity':25,'min_velocity':5,'max_fragmentation':100,'max_fuel':5000}
        candidates = prepare_candidates_for_quantum(raw_candidates, constraints)

        # Run quantum (classical fallback in this repo)
        qres = run_quantum_optimization(candidates, constraints)
        optimal_idx = qres['optimal_index']
        optimal = candidates[optimal_idx]

        aegis_state['simulation_candidates'] = candidates
        aegis_state['quantum_result'] = qres

        # Agent 3 - safety validation
        validator = mod3.SafetyValidator()
        vres = validator.validate_solution({'optimal_index': optimal_idx, 'candidates':[optimal]}, asteroid)
        verdict = 'APPROVE' if vres.get('decision','').upper().startswith('APPROV') else 'REJECT'

        aegis_state['safety_evaluation'] = {
            'verdict': 'APPROVE' if verdict=='APPROVE' else 'REJECT',
            'raw_response': vres.get('raw_response','')
        }

        aegis_state['workflow_status'] = 'COMPLETED' if verdict=='APPROVE' else 'REJECTED'

        print("\n[debug] Final result:\n")
        print(json.dumps(aegis_state, indent=2, default=str))
        return 0
    except Exception:
        print("[debug] Error while running workflow:")
        traceback.print_exc()
        return 2

if __name__ == '__main__':
    sys.exit(main())
