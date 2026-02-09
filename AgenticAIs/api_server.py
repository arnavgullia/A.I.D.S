"""
Project Aegis - FastAPI Backend Server
Provides REST API and WebSocket endpoints for frontend integration.
"""

import sys
import os
import json
import asyncio
from datetime import datetime
from typing import Dict, Any, Optional, List
from contextlib import asynccontextmanager
from dataclasses import asdict

# Add paths
BASE_PATH = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_PATH)

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn

from shared.state_schema import AegisState, create_initial_state, add_log_entry
from shared.database import (
    get_database, Asteroid, RiskAssessment, AgentLog, 
    SimulationRun, QuantumOptimizationResult, SafetyEvaluation, FinalDecision,
    InMemoryDatabase
)
from shared.config import get_config


# ============================================================================
# PYDANTIC MODELS
# ============================================================================

class AsteroidInput(BaseModel):
    """Input model for asteroid data."""
    # All fields optional to support prompt-only input
    name: Optional[str] = None
    diameter_m: Optional[float] = None
    mass_kg: Optional[float] = None
    velocity_km_s: Optional[float] = None
    composition: Optional[str] = None
    impact_probability: Optional[float] = None
    days_until_approach: Optional[int] = None
    prompt: Optional[str] = None # New field for command input


class WorkflowProgress(BaseModel):
    """Progress update for WebSocket."""
    event: str
    agent: str
    status: str
    data: Dict[str, Any]
    timestamp: str


# ============================================================================
# WEBSOCKET MANAGER
# ============================================================================

class ConnectionManager:
    """Manages WebSocket connections for real-time updates."""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        print(f"[WebSocket] New connection. Total: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        print(f"[WebSocket] Disconnected. Total: {len(self.active_connections)}")
    
    async def broadcast(self, message: dict):
        """Send message to all connected clients."""
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                pass
    
    async def send_progress(self, event: str, agent: str, status: str, data: dict):
        """Send a progress update to all clients."""
        message = {
            "event": event,
            "agent": agent,
            "status": status,
            "data": data,
            "timestamp": datetime.now().isoformat()
        }
        await self.broadcast(message)


manager = ConnectionManager()


# ============================================================================
# WORKFLOW EXECUTION (Async with WebSocket updates)
# ============================================================================

async def run_workflow_async(asteroid_id: int, asteroid_data: dict) -> AegisState:
    """
    Run the Aegis workflow with real-time WebSocket updates.
    """
    from shared.database import get_database, Asteroid
    
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
    
    # Send start event
    await manager.send_progress("workflow_started", "orchestrator", "STARTED", {
        "asteroid_id": asteroid_id,
        "asteroid_name": asteroid_data.get('name')
    })
    
    try:
        # Agent 1: Threat Assessment
        await manager.send_progress("agent_started", "agent_1", "RUNNING", {
            "message": "Analyzing threat level..."
        })
        
        # Simulate Agent 1 work (in real implementation, call the actual agent)
        await asyncio.sleep(1)

        # Agent 1: Search Logic (if prompt provided)
        if asteroid_data.get('prompt'):
            prompt = asteroid_data['prompt']
            await manager.send_progress("agent_status", "agent_1", "RUNNING", {
                "message": f"Parsing command: '{prompt}'..."
            })
            
            # Simple keyword extraction (in real agent, use LLM)
            # Find words that look like names (starting with capital letter)
            potential_names = [w for w in prompt.split() if w[0].isupper() and len(w) > 3]
            
            db = get_database()
            found_asteroid = None
            
            for name in potential_names:
                await manager.send_progress("agent_status", "agent_1", "RUNNING", {
                    "message": f"Querying database for '{name}'..."
                })
                found_asteroid = db.get_asteroid_by_name(name)
                if found_asteroid:
                    break
            
            if not found_asteroid:
                 # Fallback: try searching the whole prompt if it's short
                 if len(prompt.split()) <= 2:
                      found_asteroid = db.get_asteroid_by_name(prompt)

            if found_asteroid:
                # Update asteroid data with found info
                asteroid_data.update(asdict(found_asteroid))
                # Update DB record with the ID we are using for this run (or link them)
                # For this demo, we just use the data found
                await manager.send_progress("asteroid_found", "agent_1", "COMPLETED", asdict(found_asteroid))
                
                await manager.send_progress("agent_status", "agent_1", "RUNNING", {
                    "message": f"Target Identified: {found_asteroid.name}"
                })
            else:
                 await manager.send_progress("workflow_error", "agent_1", "ERROR", {
                    "error": f"Could not identify asteroid in database from prompt: '{prompt}'"
                })
                 return create_initial_state(asteroid_id, asteroid_data) # Return empty/initial state on error
        
        await asyncio.sleep(1)
        
        
        # Calculate threat
        mass = asteroid_data.get('mass_kg', 1e10)
        velocity = asteroid_data.get('velocity_km_s', 20)
        impact_prob = asteroid_data.get('impact_probability', 0)
        kinetic_energy_mt = (0.5 * mass * (velocity * 1000) ** 2) / (4.184e15)
        
        risk_score = min(10.0, impact_prob * 10 + (1 if asteroid_data.get('diameter_m', 0) > 100 else 0))
        requires_deflection = risk_score >= 4.0
        
        aegis_state['threat_assessment'] = {
            'impact_probability': impact_prob,
            'kinetic_energy_mt': kinetic_energy_mt,
            'estimated_damage': "Global" if kinetic_energy_mt > 1000 else "Regional",
            'risk_score': risk_score,
            'requires_deflection': requires_deflection,
            'assessment_timestamp': datetime.now().isoformat(),
        }

        # Database: Store Risk Assessment
        try:
            db.insert_risk_assessment(RiskAssessment(
                assessment_id=0,
                asteroid_id=asteroid_id,
                impact_probability=impact_prob,
                kinetic_energy_mt=kinetic_energy_mt,
                estimated_damage="Global" if kinetic_energy_mt > 1000 else "Regional",
                risk_score=risk_score,
                requires_deflection=requires_deflection
            ))
        except Exception as e:
            print(f"[Database] Error storing risk assessment: {e}")
        
        if not requires_deflection:
            aegis_state['workflow_status'] = 'COMPLETED'
            await manager.send_progress("workflow_completed", "orchestrator", "NO_ACTION", {
                "message": "Low risk - no deflection needed"
            })
            return aegis_state
        
        # Agent 2: Strategic Planning + Quantum Optimization
        await manager.send_progress("agent_started", "agent_2", "RUNNING", {
            "message": "Generating deflection strategies..."
        })
        
        await asyncio.sleep(1)
        
        # Generate candidates (Agent 2 Simulation)
        import random
        
        candidates = []
        # Generate 50+ candidates
        for i in range(50):
            # Random variations
            velocity = 5.0 + random.random() * 20.0  # 5 to 25 km/s
            angle = 10.0 + random.random() * 80.0    # 10 to 90 degrees
            mass_impactor = 500 + random.random() * 1000 # 500 to 1500 kg
            
            # Simple score calculation based on "optimal" range
            # Optimal: Velocity ~12km/s, Angle ~45deg
            v_score = 1.0 - min(1.0, abs(velocity - 12.0) / 12.0)
            a_score = 1.0 - min(1.0, abs(angle - 45.0) / 45.0)
            base_score = (v_score * 0.6 + a_score * 0.4)
            
            # Add some randomness to score
            final_score = base_score * (0.9 + random.random() * 0.2)
            final_score = max(0.1, min(0.99, final_score))
            
            # Determine validity (randomly fail some low scoring ones)
            is_valid = True
            if final_score < 0.3:
                is_valid = random.random() > 0.8
            
            candidates.append({
                'id': i, # Temporary ID
                'strategy': 'kinetic',
                'velocity_km_s': round(velocity, 2),
                'angle_degrees': round(angle, 2),
                'impactor_mass_kg': round(mass_impactor, 1),
                'estimated_fuel_kg': round(mass_impactor * 5, 1),
                'score': round(final_score, 4),
                'validity': is_valid
            })
            
        # Select Top 16 for Quantum Optimization
        # Sort by score desc, then pick top 16
        candidates.sort(key=lambda x: x['score'], reverse=True)
        top_16_candidates = candidates[:16]
        
        # Re-assign IDs 0-15 for Grover's
        final_candidates = []
        for idx, c in enumerate(top_16_candidates):
            c['original_id'] = c['id']
            c['id'] = idx
            final_candidates.append(c)
            
        candidates = final_candidates # Replace with top 16
        
        # Database: Store Simulations
        # We need a strategy ID first (placeholder for now)
        strategy_id = 999 
        try:
            for c in candidates:
                db.insert_simulation(SimulationRun(
                    simulation_id=0,
                    strategy_id=strategy_id,
                    candidate_index=c['id'],
                    velocity_km_s=c['velocity_km_s'],
                    angle_degrees=c['angle_degrees'],
                    timing_days=365, # Default
                    impactor_mass_kg=c['impactor_mass_kg'],
                    estimated_fuel_kg=c['estimated_fuel_kg'],
                    is_optimal=False
                ))
        except Exception as e:
            print(f"[Database] Error storing simulations: {e}")

        # Write to maneuver_demo.json for Quantum Backend
        try:
            demo_file_path = os.path.abspath(os.path.join(os.path.dirname(BASE_PATH), "Quantum_Grover", "maneuver_demo.json"))
            print(f"[Agent 2] Writing to: {demo_file_path}")
            
            # Format strictly for GroverAlgo.py: {"maneuvers": [{"id":..., "score":..., "validity":...}]}
            grover_data = {
                "maneuvers": [
                    {
                        "id": c['id'],
                        "score": c['score'],
                        "validity": c['validity']
                    }
                    for c in candidates
                ]
            }
            
            with open(demo_file_path, "w") as f:
                json.dump(grover_data, f, indent=2)
                
            print(f"[Agent 2] Successfully updated maneuver_demo.json")
            
        except Exception as e:
            print(f"[Agent 2] Error writing maneuver_demo.json: {e}")
            # Continue workflow even if file write fails
        
        await manager.send_progress("candidates_generated", "agent_2", "RUNNING", {
            "message": "Running quantum optimization...",
            "candidate_count": 16,
            "candidates": candidates # Send full list to frontend
        })
        
        await asyncio.sleep(2)
        
        # Quantum optimization
        from shared.quantum_integration import run_quantum_optimization
        
        try:
            quantum_result = run_quantum_optimization(candidates)
            optimal_idx = quantum_result['optimal_index']
        except Exception as e:
            # Classical fallback
            valid_candidates = [c for c in candidates if c.get('validity', True)]
            optimal_idx = max(range(len(candidates)), key=lambda i: candidates[i].get('score', 0))
            quantum_result = {
                'optimal_index': optimal_idx,
                'success_probability': 1.0,
                'qubits_used': 0,
                'iterations': 16,
                'quantum_advantage': 1.0,
                'is_classical_fallback': True
            }
        
        optimal_candidate = candidates[optimal_idx]
        
        # Database: Store Quantum Result
        try:
            db.insert_quantum_result(QuantumOptimizationResult(
                result_id=0,
                asteroid_id=asteroid_id,
                optimal_simulation_id=0, # Need to link back to simulation ID in real app
                optimal_index=optimal_idx,
                success_probability=quantum_result.get('success_probability', 0.85),
                qubits_used=quantum_result.get('qubits_used', 4),
                iterations=quantum_result.get('iterations', 3),
                quantum_advantage=quantum_result.get('quantum_advantage', 4.0),
                execution_time_ms=quantum_result.get('execution_time_ms', 0)
            ))
        except Exception as e:
            print(f"[Database] Error storing quantum result: {e}")

        aegis_state['simulation_candidates'] = candidates
        aegis_state['quantum_result'] = {
            'optimal_index': optimal_idx,
            'optimal_solution': optimal_candidate,
            'success_probability': quantum_result.get('success_probability', 0.85),
            'qubits_used': quantum_result.get('qubits_used', 4),
            'iterations': quantum_result.get('iterations', 3),
            'quantum_advantage': quantum_result.get('quantum_advantage', 4.0),
            'execution_time_ms': quantum_result.get('execution_time_ms', 0),
        }
        
        await manager.send_progress("agent_completed", "agent_2", "COMPLETED", {
            "optimal_index": optimal_idx,
            "optimal_velocity": optimal_candidate['velocity_km_s'],
            "optimal_angle": optimal_candidate['angle_degrees'],
            "quantum_advantage": quantum_result.get('quantum_advantage', 4.0),
            "success_probability": quantum_result.get('success_probability', 0.85)
        })
        
        # Agent 3: Safety Validation
        await manager.send_progress("agent_started", "agent_3", "RUNNING", {
            "message": "Validating solution safety..."
        })
        
        await asyncio.sleep(1.5)
        
        # Safety checks
        velocity = optimal_candidate['velocity_km_s']
        fragmentation_risk = (velocity / 20) * 60  # Simple estimate
        miss_distance_km = 15000 + (optimal_idx * 500)
        confidence = quantum_result.get('success_probability', 0.85) * 100
        
        # Decision logic
        verdict = "APPROVE" if (fragmentation_risk < 100 and miss_distance_km > 10000 and confidence > 75) else "REJECT"
        
        # Database: Store Safety Evaluation
        try:
            db.insert_safety_evaluation(SafetyEvaluation(
                evaluation_id=0,
                simulation_id=0, # Placeholder
                fragmentation_risk_pct=round(fragmentation_risk, 2),
                miss_distance_km=miss_distance_km,
                confidence_score=confidence,
                verdict=verdict,
                failed_checks_json="[]"
            ))
        except Exception as e:
            print(f"[Database] Error storing safety evaluation: {e}")

        aegis_state['safety_evaluation'] = {
            'fragmentation_risk_pct': round(fragmentation_risk, 2),
            'miss_distance_km': miss_distance_km,
            'confidence_score': confidence,
            'verdict': verdict,
            'failed_checks': [],
            'evaluation_timestamp': datetime.now().isoformat(),
        }
        
        await manager.send_progress("agent_completed", "agent_3", "COMPLETED", {
            "verdict": verdict,
            "fragmentation_risk_pct": round(fragmentation_risk, 2),
            "miss_distance_km": miss_distance_km,
            "confidence_score": confidence
        })
        
        # Final decision
        aegis_state['workflow_status'] = 'COMPLETED' if verdict == "APPROVE" else 'REJECTED'
        
        # Database: Store Final Decision
        try:
            db.insert_final_decision(FinalDecision(
                decision_id=0,
                asteroid_id=asteroid_id,
                strategy_id=999,
                primary_simulation_id=0,
                backup_simulation_id=None,
                confidence_score=confidence,
                explanation=f"Automated decision based on safety check: {verdict}",
                approved_by_humans=False
            ))
        except Exception as e:
            print(f"[Database] Error storing final decision: {e}")

        await manager.send_progress("workflow_completed", "orchestrator", 
                                    "APPROVED" if verdict == "APPROVE" else "REJECTED", {
            "final_verdict": verdict,
            "optimal_solution": optimal_candidate,
            "quantum_advantage": quantum_result.get('quantum_advantage', 4.0)
        })
        
    except Exception as e:
        await manager.send_progress("workflow_error", "orchestrator", "ERROR", {
            "error": str(e)
        })
        aegis_state['workflow_status'] = 'ERROR'
    
    return aegis_state


# ============================================================================
# FASTAPI APP
# ============================================================================

# Store running workflows
active_workflows: Dict[int, Dict[str, Any]] = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    print("[API] Project Aegis API Server starting...")
    db = get_database()
    db.connect()
    
    if isinstance(db, InMemoryDatabase):
        print("======== WARNING: USING IN-MEMORY DATABASE (Testing Only) ========")
        print("To use MySQL, set AEGIS_DB_TYPE=mysql in environment variables.")
        print("==================================================================")
        
    # SEED DATA for In-Memory Database
    # This ensures "Apophis" exists and has high enough risk to trigger Agent 2
    if isinstance(db, InMemoryDatabase):
        print("[API] Seeding In-Memory Database with demo data...")
        demo_data = await get_demo_asteroids()
        for key, asteroid_dict in demo_data.items():
            # Check if exists
            if not db.get_asteroid_by_name(asteroid_dict['name']):
                from shared.database import Asteroid
                a = Asteroid(
                    asteroid_id=0, # Auto-gen
                    name=asteroid_dict['name'],
                    diameter_m=asteroid_dict['diameter_m'],
                    mass_kg=asteroid_dict['mass_kg'],
                    velocity_km_s=asteroid_dict['velocity_km_s'],
                    composition=asteroid_dict['composition'],
                    impact_probability=asteroid_dict['impact_probability'],
                    days_until_approach=asteroid_dict['days_until_approach']
                )
                db.insert_asteroid(a)
                print(f"[API] Seeded: {a.name}")
    
    yield
    print("[API] Server shutting down...")


app = FastAPI(
    title="Project Aegis API",
    description="Multi-Agent Planetary Defense System API",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# REST ENDPOINTS
# ============================================================================

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "Project Aegis API",
        "version": "1.0.0",
        "status": "online",
        "endpoints": {
            "POST /analyze": "Start asteroid analysis",
            "GET /status/{id}": "Get workflow status",
            "GET /demo": "Get demo asteroid data",
            "WS /ws": "WebSocket for real-time updates"
        }
    }


@app.get("/demo")
async def get_demo_asteroids():
    """Get predefined demo asteroids."""
    return {
        "demo1": {
            "name": "Apophis-99942",
            "diameter_m": 340,
            "mass_kg": 2.7e10,
            "velocity_km_s": 30.0,
            "composition": "Stony-Iron",
            "impact_probability": 0.45,
            "days_until_approach": 1000,
            "description": "High-risk asteroid"
        },
        "demo2": {
            "name": "Small-Rock-001",
            "diameter_m": 30,
            "mass_kg": 1e7,
            "velocity_km_s": 15.0,
            "composition": "Stony",
            "impact_probability": 0.001,
            "days_until_approach": 3650,
            "description": "Low-risk asteroid"
        },
        "demo3": {
            "name": "Bennu-101955",
            "diameter_m": 500,
            "mass_kg": 7.3e10,
            "velocity_km_s": 28.0,
            "composition": "Rubble Pile",
            "impact_probability": 0.05,
            "days_until_approach": 36500,
            "description": "High-threat rubble pile"
        },
        "demo4": {
            "name": "Xerxes-2029",
            "diameter_m": 1200,
            "mass_kg": 4.5e11,
            "velocity_km_s": 18.5,
            "composition": "Iron-Nickel",
            "impact_probability": 0.95,
            "days_until_approach": 150,
            "description": "EXTREME THREAT: Planet killer"
        },
        "demo5": {
            "name": "Icarus-2025",
            "diameter_m": 85,
            "mass_kg": 3.2e8,
            "velocity_km_s": 42.0,
            "composition": "Ice-Rock",
            "impact_probability": 0.12,
            "days_until_approach": 800,
            "description": "Fast mover, potential airburst"
        },
        "demo6": {
            "name": "Didymos-65803",
            "diameter_m": 780,
            "mass_kg": 5.2e11,
            "velocity_km_s": 22.1,
            "composition": "Silicate",
            "impact_probability": 0.15,
            "days_until_approach": 2500,
            "description": "Binary system primary"
        },
        "demo7": {
            "name": "Dimorphos-B",
            "diameter_m": 160,
            "mass_kg": 4.8e9,
            "velocity_km_s": 22.1,
            "composition": "Silicate",
            "impact_probability": 0.08,
            "days_until_approach": 2500,
            "description": "Binary system moonlet"
        },
        "demo8": {
            "name": "2023-DW",
            "diameter_m": 50,
            "mass_kg": 2e8,
            "velocity_km_s": 24.0,
            "composition": "Stony",
            "impact_probability": 0.002,
            "days_until_approach": 7800,
            "description": "Recent discovery, low risk"
        },
        "demo9": {
            "name": "Hermes-1937",
            "diameter_m": 400,
            "mass_kg": 5e10,
            "velocity_km_s": 35.0,
            "composition": "Monolith",
            "impact_probability": 0.35,
            "days_until_approach": 400,
            "description": "Erratic orbit, high concern"
        },
        "demo10": {
            "name": "Zephyr-Fast",
            "diameter_m": 20,
            "mass_kg": 5e6,
            "velocity_km_s": 65.0,
            "composition": "Unknown",
            "impact_probability": 0.01,
            "days_until_approach": 45,
            "description": "Hypervelocity object"
        }
    }


@app.post("/analyze")
async def analyze_asteroid(asteroid: AsteroidInput):
    """
    Start asteroid analysis workflow.
    Returns workflow ID for tracking progress via WebSocket.
    """
    # Generate unique ID
    asteroid_id = int(datetime.now().timestamp() * 1000) % 1000000
    
    asteroid_data = asteroid.model_dump()
    
    # Store workflow reference
    active_workflows[asteroid_id] = {
        "status": "STARTED",
        "started_at": datetime.now().isoformat(),
        "asteroid_data": asteroid_data
    }
    
    # Start workflow in background
    asyncio.create_task(run_workflow_async(asteroid_id, asteroid_data))
    
    return {
        "workflow_id": asteroid_id,
        "message": "Analysis started",
        "websocket_url": f"/ws"
    }


@app.get("/status/{workflow_id}")
async def get_workflow_status(workflow_id: int):
    """Get status of a running or completed workflow."""
    if workflow_id not in active_workflows:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    return active_workflows[workflow_id]


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


# ============================================================================
# WEBSOCKET ENDPOINT
# ============================================================================

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time workflow updates.
    
    Events sent:
    - workflow_started
    - agent_started
    - agent_completed
    - candidates_generated
    - workflow_completed
    - workflow_error
    """
    await manager.connect(websocket)
    
    try:
        # Send connection confirmation
        await websocket.send_json({
            "event": "connected",
            "message": "Connected to Aegis real-time updates",
            "timestamp": datetime.now().isoformat()
        })
        
        # Keep connection alive and listen for client messages
        while True:
            try:
                data = await websocket.receive_text()
                # Handle client commands if needed
                if data == "ping":
                    await websocket.send_json({"event": "pong"})
            except WebSocketDisconnect:
                break
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("  PROJECT AEGIS - API SERVER")
    print("=" * 60)
    print("\nStarting server on http://localhost:8000")
    print("WebSocket available at ws://localhost:8000/ws")
    print("\nPress Ctrl+C to stop\n")
    
    uvicorn.run(
        "api_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
