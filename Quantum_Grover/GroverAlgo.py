import json
import math
import random
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator

def flexible_grover_oracle(n_qubits, target_indices):
    qc = QuantumCircuit(n_qubits)
    for idx in target_indices:
        target_bin = format(idx, f'0{n_qubits}b')[::-1]
        for i, bit in enumerate(target_bin):
            if bit == '0': qc.x(i)
        
        # Phase flip
        qc.h(n_qubits - 1)
        qc.mcx(list(range(n_qubits - 1)), n_qubits - 1)
        qc.h(n_qubits - 1)
        
        for i, bit in enumerate(target_bin):
            if bit == '0': qc.x(i)
    return qc

def diffuser(n_qubits):
    qc = QuantumCircuit(n_qubits)
    qc.h(range(n_qubits))
    qc.x(range(n_qubits))
    qc.h(n_qubits - 1)
    qc.mcx(list(range(n_qubits - 1)), n_qubits - 1)
    qc.h(n_qubits - 1)
    qc.x(range(n_qubits))
    qc.h(range(n_qubits))
    return qc

def find_max_quantum(data_list, target_key='score'):
    N = len(data_list)
    if N == 0: return None
    
    n_qubits = math.ceil(math.log2(N))
    # Ideal simulator (no noise model provided)
    backend = AerSimulator()
    
    valid_items = [i for i, item in enumerate(data_list) if item.get('validity') is True]
    if not valid_items: return None
    
    current_best_idx = random.choice(valid_items)
    
    # Dürr-Høyer iterative improvement
    for _ in range(int(math.sqrt(N)) + 1):
        threshold = data_list[current_best_idx][target_key]
        better_indices = [
            i for i, item in enumerate(data_list) 
            if item.get(target_key, 0) > threshold and item.get('validity') is True
        ]
        
        if not better_indices: break
            
        qc = QuantumCircuit(n_qubits, n_qubits)
        qc.h(range(n_qubits))
        
        # Calculate optimal Grover iterations for M matches
        # M = len(better_indices), N_space = 2^n_qubits
        steps = max(1, round((math.pi/4) * math.sqrt((2**n_qubits)/len(better_indices))))
        
        oracle = flexible_grover_oracle(n_qubits, better_indices)
        diff = diffuser(n_qubits)
        
        for _ in range(steps):
            qc.compose(oracle, inplace=True)
            qc.compose(diff, inplace=True)
            
        qc.measure(range(n_qubits), range(n_qubits))
        
        # Transpile for the ideal backend
        tqc = transpile(qc, backend)
        # Using 1 shot could theoretically work in an ideal scenario, 
        # but 256 ensures we catch the peak of the probability distribution.
        counts = backend.run(tqc, shots=256).result().get_counts()
        measured_idx = int(max(counts, key=counts.get), 2)
        
        if measured_idx < N:
            item = data_list[measured_idx]
            if item.get('validity') is True and item.get(target_key, 0) > threshold:
                current_best_idx = measured_idx

    return data_list[current_best_idx]

def run_maneuver_search(file_path):
    try:
        with open(file_path, 'r') as f:
            data_list = json.load(f)
            # Basic normalization if JSON is wrapped in a dict
            if isinstance(data_list, dict):
                data_list = data_list.get('maneuvers', list(data_list.values())[0])
                
        winner = find_max_quantum(data_list, 'score')
        print(json.dumps(winner, indent=4) if winner else "No valid results.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    # Ensure 'maneuver_demo.json' exists in your directory
    run_maneuver_search('maneuver_demo.json')