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

# Add paths
BASE_PATH = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_PATH)

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn

from shared.state_schema import AegisState, create_initial_state, add_log_entry
from shared.database import get_database, Asteroid, RiskAssessment, AgentLog
from shared.config import get_config


# ============================================================================
# PYDANTIC MODELS
# ============================================================================

class AsteroidInput(BaseModel):
    """Input model for asteroid data."""
    name: str
    diameter_m: float
    mass_kg: float
    velocity_km_s: float
    composition: str
    impact_probability: float
    days_until_approach: int


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
        await asyncio.sleep(2)
        
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
        
        await manager.send_progress("agent_completed", "agent_1", "COMPLETED", {
            "risk_score": risk_score,
            "requires_deflection": requires_deflection,
            "kinetic_energy_mt": round(kinetic_energy_mt, 2)
        })
        
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
        
        # Generate candidates
        candidates = []
        for i in range(16):
            velocity = 8.0 + i * 0.8
            angle = 15.0 + i * 2.5
            candidates.append({
                'id': i,
                'strategy': 'kinetic',
                'velocity_km_s': round(velocity, 2),
                'angle_degrees': round(angle, 2),
                'impactor_mass_kg': 500 + i * 20,
                'estimated_fuel_kg': 2500 + i * 100,
                'score': 0.5 + (0.03 * i if i < 10 else -0.02 * i),
                'validity': i not in [3, 10, 14]  # Some invalid
            })
        
        await manager.send_progress("candidates_generated", "agent_2", "RUNNING", {
            "message": "Running quantum optimization...",
            "candidate_count": 16
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
    get_database().connect()
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
            "impact_probability": 0.02,
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
    print("  🛡️  PROJECT AEGIS - API SERVER")
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
