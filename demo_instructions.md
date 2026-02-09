# Project Aegis - Demo Instructions

You requested materials for a demo video. Here is everything you need.

## 1. Sample Data (Pre-loaded)
The following 10 "Asteroid Scenarios" have been pre-loaded into the system. You can trigger them by typing their names into the **Command Center** on the dashboard.

| Command / Name | Type | Risk Level | Outcome |
| :--- | :--- | :--- | :--- |
| **Apophis-99942** | Stony-Iron | High | **Target Locked** (High Probability) |
| **Small-Rock-001** | Stony | Low | No Action Needed |
| **Bennu-101955** | Rubble Pile | Medium | **Target Locked** |
| **Xerxes-2029** | Iron-Nickel | **EXTREME** | **PLANET KILLER** (Requires Deflection) |
| **Icarus-2025** | Ice-Rock | Medium | Fast Mover |
| **Didymos-65803** | Silicate | Medium | Binary System |
| **Dimorphos-B** | Silicate | Low | Moonlet |
| **2023-DW** | Stony | Low | Monitor Only |
| **Hermes-1937** | Monolith | High | Erratic Orbit |
| **Zephyr-Fast** | Unknown | Low | Hypervelocity |

**How to use:**
1. Open the frontend (`http://localhost:5173`).
2. Type one of the names above (e.g., `Xerxes-2029`) into the text box.
3. Click "Initialize Sequence".

## 2. Quantum Search Histogram
A sample histogram from the Grover's Algorithm search has been generated for you.
- File: `quantum_histogram.png` (in the root directory: `/home/pranjay/workspace/A.I.D.S/quantum_histogram.png`)

You can use this image directly in your video or presentation if the live quantum simulation is too fast to see.

## 3. Running the Demo
1. Ensure the API Server is running:
   ```bash
   cd "Antigravity-AgenticAIs copy"
   source venv/bin/activate
   python api_server.py
   ```
2. Ensure the Frontend is running:
   ```bash
   cd "Antigravity-FrontendSample copy"
   npm run dev
   ```
3. Ensure the Quantum Server is running (optional, for live quantum button):
   ```bash
   cd "Quantum_Grover"
   python server.py
   ```
