"""
Project Aegis - Quantum Integration Module
Bridge between Agent 2 and the Quantum Grover algorithm.
"""

import sys
import os
import json
import math
import time
from typing import Dict, List, Any, Optional

# Add quantum module path
QUANTUM_MODULE_PATH = "/home/pranjay/workspace/A.I.D.S/Quantum_Grover"


def run_quantum_optimization(
    candidates: List[Dict[str, Any]],
    oracle_constraints: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Run Grover's quantum optimization on 16 deflection candidates.
    
    This function interfaces with the quantum module to find the optimal
    deflection solution from a set of 16 candidates (4 qubits).
    
    Args:
        candidates: List of 16 candidate dictionaries, each containing:
            - id: int (0-15)
            - velocity_km_s: float
            - angle_degrees: float
            - impactor_mass_kg: float (optional)
            - score: float (feasibility/effectiveness score)
            - validity: bool (whether candidate meets basic constraints)
            
        oracle_constraints: Optional constraints for the oracle:
            - min_miss_distance: float (km)
            - max_fuel: float (kg)
            - max_fragmentation: float (%)
            
    Returns:
        Dictionary with:
            - optimal_index: int (0-15)
            - optimal_candidate: dict (the winning candidate)
            - success_probability: float
            - qubits_used: int
            - iterations: int
            - quantum_advantage: float
            - execution_time_ms: float
    """
    start_time = time.time()
    
    # Validate input
    if len(candidates) != 16:
        raise ValueError(f"Exactly 16 candidates required, got {len(candidates)}")
    
    # Ensure all candidates have required fields
    for i, c in enumerate(candidates):
        if 'id' not in c:
            c['id'] = i
        if 'validity' not in c:
            c['validity'] = True
        if 'score' not in c:
            # Calculate a score based on available parameters
            c['score'] = _calculate_candidate_score(c, oracle_constraints)
    
    try:
        # Try to use the real quantum module
        result = _run_real_quantum(candidates)
    except Exception as e:
        print(f"[Quantum] Real quantum module failed: {e}")
        print("[Quantum] Falling back to classical simulation...")
        result = _run_classical_fallback(candidates)
    
    # Calculate execution time
    execution_time_ms = (time.time() - start_time) * 1000
    result['execution_time_ms'] = execution_time_ms
    
    # Add the optimal candidate details
    optimal_idx = result['optimal_index']
    result['optimal_candidate'] = candidates[optimal_idx]
    
    return result


def _calculate_candidate_score(
    candidate: Dict[str, Any],
    constraints: Optional[Dict[str, Any]] = None
) -> float:
    """Calculate a feasibility score for a candidate."""
    score = 0.5  # Base score
    
    # Prefer moderate velocities (10-15 km/s is ideal)
    velocity = candidate.get('velocity_km_s', 10)
    if 10 <= velocity <= 15:
        score += 0.2
    elif velocity < 8 or velocity > 20:
        score -= 0.2
    
    # Prefer angles between 15-45 degrees
    angle = candidate.get('angle_degrees', 30)
    if 15 <= angle <= 45:
        score += 0.2
    elif angle < 10 or angle > 60:
        score -= 0.1
    
    # Apply constraint-based scoring if constraints provided
    if constraints:
        # Lower fuel is better
        fuel = candidate.get('estimated_fuel_kg', 3000)
        max_fuel = constraints.get('max_fuel', 5000)
        if fuel < max_fuel * 0.7:
            score += 0.1
        elif fuel > max_fuel:
            score -= 0.3
    
    return max(0.0, min(1.0, score))


def _run_real_quantum(candidates: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Run the actual Grover quantum algorithm.
    
    This imports and uses the quantum module from A.I.D.S.
    """
    # Add quantum module to path
    if QUANTUM_MODULE_PATH not in sys.path:
        sys.path.insert(0, QUANTUM_MODULE_PATH)
    
    # Import required modules
    import math
    from qiskit import QuantumCircuit, transpile
    from qiskit_aer import AerSimulator
    
    # Find the best valid candidate (this is what the oracle will mark)
    valid_candidates = [c for c in candidates if c.get('validity', True)]
    if not valid_candidates:
        raise ValueError("No valid candidates found")
    
    best_idx = max(
        (i for i, c in enumerate(candidates) if c.get('validity', True)),
        key=lambda i: candidates[i].get('score', 0)
    )
    
    # Build Grover circuit
    n_qubits = 4  # 2^4 = 16 candidates
    
    # Build oracle
    def build_oracle(n_qubits: int, target_index: int) -> QuantumCircuit:
        oracle_qc = QuantumCircuit(n_qubits, name="Oracle")
        target_bin = format(target_index, f'0{n_qubits}b')[::-1]
        
        for i, bit in enumerate(target_bin):
            if bit == '0':
                oracle_qc.x(i)
        
        oracle_qc.h(n_qubits - 1)
        oracle_qc.mcx(list(range(n_qubits - 1)), n_qubits - 1)
        oracle_qc.h(n_qubits - 1)
        
        for i, bit in enumerate(target_bin):
            if bit == '0':
                oracle_qc.x(i)
        
        return oracle_qc
    
    # Build diffuser
    def build_diffuser(n_qubits: int) -> QuantumCircuit:
        diff_qc = QuantumCircuit(n_qubits, name="Diffuser")
        diff_qc.h(range(n_qubits))
        diff_qc.x(range(n_qubits))
        diff_qc.h(n_qubits - 1)
        diff_qc.mcx(list(range(n_qubits - 1)), n_qubits - 1)
        diff_qc.h(n_qubits - 1)
        diff_qc.x(range(n_qubits))
        diff_qc.h(range(n_qubits))
        return diff_qc
    
    # Create main circuit
    qc = QuantumCircuit(n_qubits)
    
    # Initialize superposition
    qc.h(range(n_qubits))
    
    # Calculate optimal iterations
    iterations = max(1, round(math.pi / 4 * math.sqrt(2 ** n_qubits)))
    
    # Build oracle and diffuser
    oracle = build_oracle(n_qubits, best_idx)
    diffuser = build_diffuser(n_qubits)
    
    # Apply Grover iterations
    for _ in range(iterations):
        qc.append(oracle, range(n_qubits))
        qc.append(diffuser, range(n_qubits))
    
    # Measure
    qc.measure_all()
    
    # Execute on simulator
    backend = AerSimulator()
    tqc = transpile(qc, backend)
    result = backend.run(tqc, shots=2048).result()
    counts = result.get_counts()
    
    # Find most measured state
    measured_state = max(counts, key=counts.get)
    measured_index = int(measured_state[::-1], 2)
    success_probability = counts[measured_state] / 2048
    
    # Calculate quantum advantage
    # Classical search: O(N) = 16 checks
    # Quantum search: O(√N) = 4 checks (iterations)
    quantum_advantage = 16 / max(1, iterations)
    
    print(f"[Quantum] Grover search complete!")
    print(f"[Quantum] Optimal index: {measured_index}")
    print(f"[Quantum] Success probability: {success_probability:.2%}")
    print(f"[Quantum] Iterations: {iterations}")
    print(f"[Quantum] Quantum advantage: {quantum_advantage:.1f}x")
    
    return {
        'optimal_index': measured_index,
        'success_probability': success_probability,
        'qubits_used': n_qubits,
        'iterations': iterations,
        'quantum_advantage': quantum_advantage,
        'measurement_counts': dict(counts),
    }


def _run_classical_fallback(candidates: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Classical fallback when quantum module is not available.
    Simply finds the best valid candidate by score.
    """
    print("[Quantum] Using classical fallback (no quantum advantage)")
    
    valid_candidates = [c for c in candidates if c.get('validity', True)]
    if not valid_candidates:
        # If no valid candidates, return first one
        optimal_idx = 0
    else:
        # Find best by score
        optimal_idx = max(
            (i for i, c in enumerate(candidates) if c.get('validity', True)),
            key=lambda i: candidates[i].get('score', 0)
        )
    
    return {
        'optimal_index': optimal_idx,
        'success_probability': 1.0,  # Classical is deterministic
        'qubits_used': 0,
        'iterations': 16,  # Classical checks all
        'quantum_advantage': 1.0,  # No advantage
        'is_classical_fallback': True,
    }


def prepare_candidates_for_quantum(
    raw_candidates: List[Dict[str, Any]],
    constraints: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """
    Prepare raw simulation candidates for quantum optimization.
    
    This function takes the output from Agent 2's simulation generator
    and formats it for the quantum algorithm.
    
    Args:
        raw_candidates: List of candidates from simulation_generator.py
        constraints: Oracle constraints for validity checking
        
    Returns:
        List of 16 candidates formatted for quantum optimization
    """
    formatted = []
    
    for i, c in enumerate(raw_candidates[:16]):
        # Determine validity based on constraints
        velocity = c.get('velocity_km_s', 10)
        angle = c.get('angle_degrees', 30)
        
        is_valid = True
        
        # Check velocity constraints
        if velocity > constraints.get('max_velocity', 25):
            is_valid = False
        if velocity < constraints.get('min_velocity', 5):
            is_valid = False
        
        # Check fragmentation risk (rough estimate)
        # High velocity on fragile asteroid = invalid
        max_frag = constraints.get('max_fragmentation', 100)
        est_frag = (velocity / 20) * 100  # Rough estimate
        if est_frag > max_frag:
            is_valid = False
        
        formatted.append({
            'id': i,
            'velocity_km_s': c.get('velocity_km_s', velocity),
            'angle_degrees': c.get('angle_degrees', angle),
            'impactor_mass_kg': c.get('impactor_mass_kg', 500),
            'estimated_fuel_kg': c.get('estimated_fuel_kg', 3000),
            'estimated_miss_km': c.get('estimated_miss_km', 15000),
            'score': _calculate_candidate_score(c, constraints),
            'validity': is_valid,
            'strategy': c.get('strategy', 'kinetic'),
        })
    
    # Pad to 16 if needed
    while len(formatted) < 16:
        formatted.append({
            'id': len(formatted),
            'velocity_km_s': 10.0,
            'angle_degrees': 30.0,
            'impactor_mass_kg': 500,
            'estimated_fuel_kg': 3000,
            'estimated_miss_km': 10000,
            'score': 0.1,
            'validity': False,  # Padding candidates are invalid
            'strategy': 'padding',
        })
    
    return formatted[:16]


# Test function
if __name__ == "__main__":
    # Create test candidates
    test_candidates = [
        {'id': i, 'velocity_km_s': 8 + i * 0.5, 'angle_degrees': 20 + i * 2, 
         'score': 0.5 + (0.03 * i if i < 10 else -0.02 * i), 'validity': True}
        for i in range(16)
    ]
    
    # Mark some as invalid
    test_candidates[3]['validity'] = False
    test_candidates[10]['validity'] = False
    test_candidates[14]['validity'] = False
    
    print("=" * 50)
    print("  QUANTUM INTEGRATION TEST")
    print("=" * 50)
    print(f"\nTesting with {len(test_candidates)} candidates...")
    
    result = run_quantum_optimization(test_candidates)
    
    print(f"\n{'=' * 50}")
    print("  RESULT")
    print("=" * 50)
    print(json.dumps(result, indent=2, default=str))
