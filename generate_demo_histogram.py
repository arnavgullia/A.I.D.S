
import json
import base64
import os
import sys

# Add path to include Quantum_Grover module
sys.path.append(os.path.join(os.getcwd(), 'Quantum_Grover'))

try:
    import GroverAlgo
except ImportError:
    # Fallback if running from root
    sys.path.append(os.path.join(os.getcwd(), 'A.I.D.S', 'Quantum_Grover'))
    import GroverAlgo

def generate_histogram():
    # 1. Create a dummy maneuver file if it doesn't exist or just to be sure we have good data
    dummy_data = {
        "maneuvers": [
            {"id": 0, "score": 0.25, "validity": True},
            {"id": 1, "score": 0.45, "validity": True},
            {"id": 2, "score": 0.30, "validity": True},
            {"id": 3, "score": 0.10, "validity": True},
            {"id": 4, "score": 0.85, "validity": True}, # Target
            {"id": 5, "score": 0.20, "validity": True},
            {"id": 6, "score": 0.15, "validity": True},
            {"id": 7, "score": 0.35, "validity": True}
        ]
    }
    
    demo_file = 'demo_maneuver_data.json'
    with open(demo_file, 'w') as f:
        json.dump(dummy_data, f)
        
    print(f"Created temporary file: {demo_file}")
    
    # 2. Run Grover Algo
    print("Running Quantum Search...")
    result = GroverAlgo.run_quantum_maneuver_search(demo_file, return_image=True)
    
    if result and 'plot_image' in result:
        # 3. Decode and save image
        data_uri = result['plot_image']
        # Remove header "data:image/png;base64,"
        base64_data = data_uri.split(',')[1]
        
        output_file = 'quantum_histogram.png'
        with open(output_file, 'wb') as f:
            f.write(base64.decodebytes(base64_data.encode()))
            
        print(f"Success! Histogram saved to: {os.path.abspath(output_file)}")
    else:
        print("Failed to generate histogram.")

    # Cleanup
    if os.path.exists(demo_file):
        os.remove(demo_file)

if __name__ == "__main__":
    generate_histogram()
