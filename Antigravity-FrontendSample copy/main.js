/**
 * Project Aegis - Frontend JavaScript
 * Handles WebSocket connection, form submission, and UI updates
 */

// API Configuration
const API_BASE = 'http://localhost:8000';
const WS_URL = 'ws://localhost:8000/ws';

// State
let websocket = null;
let isConnected = false;
let isAnalyzing = false;

// Demo asteroid data
const demoAsteroids = {
    demo1: {
        name: "Apophis-99942",
        diameter_m: 340,
        mass_kg: 2.7e10,
        velocity_km_s: 30.0,
        composition: "Stony-Iron",
        impact_probability: 0.02,
        days_until_approach: 1000
    },
    demo2: {
        name: "Small-Rock-001",
        diameter_m: 30,
        mass_kg: 1e7,
        velocity_km_s: 15.0,
        composition: "Stony",
        impact_probability: 0.001,
        days_until_approach: 3650
    },
    demo3: {
        name: "Bennu-101955",
        diameter_m: 500,
        mass_kg: 7.3e10,
        velocity_km_s: 28.0,
        composition: "Rubble Pile",
        impact_probability: 0.05,
        days_until_approach: 36500
    }
};

// ============================================================================
// INITIALIZATION
// ============================================================================

document.addEventListener('DOMContentLoaded', () => {
    initScrollEffects();
    initForm();
    initDemoButtons();
    connectWebSocket();

    console.log('Project Aegis: Frontend initialized');
});

// ============================================================================
// SCROLL EFFECTS
// ============================================================================

function initScrollEffects() {
    const videoBg = document.getElementById('video-bg');
    const contentSection = document.getElementById('dashboard');
    const mainTitle = document.getElementById('main-title');
    const subtitle = document.getElementById('subtitle');
    const titleContainer = document.getElementById('title-container');
    const topBar = document.getElementById('top-bar');

    const fadeEnd = window.innerHeight;
    let ticking = false;

    window.addEventListener('scroll', () => {
        if (!ticking) {
            window.requestAnimationFrame(() => {
                updateScrollEffects();
                ticking = false;
            });
            ticking = true;
        }
    });

    function updateScrollEffects() {
        const scrollY = window.scrollY;
        let progress = Math.min(Math.max(scrollY / fadeEnd, 0), 1);

        // Video fade
        videoBg.style.opacity = 1 - progress;

        // Content section fade in
        contentSection.style.opacity = Math.max(0, (progress - 0.3) * 1.43);
        if (progress >= 0.7) {
            contentSection.style.opacity = 1;
        }

        // Title fade out
        const titleOpacity = Math.max(0, 1 - (progress * 3));
        mainTitle.style.opacity = titleOpacity;
        subtitle.style.opacity = titleOpacity;

        // Hide container
        if (progress > 0.35) {
            titleContainer.style.visibility = 'hidden';
        } else {
            titleContainer.style.visibility = 'visible';
        }

        // Top bar fade in
        topBar.style.opacity = progress;
        if (progress > 0.1) {
            topBar.classList.add('visible');
        } else {
            topBar.classList.remove('visible');
        }
    }

    updateScrollEffects();
}

// ============================================================================
// WEBSOCKET
// ============================================================================

function connectWebSocket() {
    try {
        websocket = new WebSocket(WS_URL);

        websocket.onopen = () => {
            console.log('[WebSocket] Connected');
            isConnected = true;
            updateConnectionStatus(true);
        };

        websocket.onclose = () => {
            console.log('[WebSocket] Disconnected');
            isConnected = false;
            updateConnectionStatus(false);

            // Reconnect after 3 seconds
            setTimeout(connectWebSocket, 3000);
        };

        websocket.onerror = (error) => {
            console.error('[WebSocket] Error:', error);
            updateConnectionStatus(false);
        };

        websocket.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                handleWebSocketMessage(data);
            } catch (e) {
                console.error('[WebSocket] Parse error:', e);
            }
        };
    } catch (error) {
        console.error('[WebSocket] Connection failed:', error);
        updateConnectionStatus(false);
        setTimeout(connectWebSocket, 3000);
    }
}

function updateConnectionStatus(connected) {
    const statusEl = document.getElementById('connection-status');
    const textEl = statusEl.querySelector('.status-text');

    if (connected) {
        statusEl.className = 'status-connected';
        textEl.textContent = 'Connected';
    } else {
        statusEl.className = 'status-disconnected';
        textEl.textContent = 'Disconnected';
    }
}

function handleWebSocketMessage(data) {
    console.log('[WebSocket] Message:', data);

    switch (data.event) {
        case 'connected':
            console.log('[WebSocket] Server confirmed connection');
            break;

        case 'workflow_started':
            showResults();
            resetAgentSteps();
            updateVerdict('analyzing', '⏳', 'Analyzing...');
            break;

        case 'agent_started':
            updateAgentStatus(data.agent, 'running', data.data.message || 'Processing...');
            break;

        case 'agent_completed':
            updateAgentStatus(data.agent, 'completed', 'Complete');
            updateAgentResult(data.agent, data.data);
            break;

        case 'candidates_generated':
            updateAgentStatus('agent_2', 'running', 'Running quantum optimization...');
            document.getElementById('quantum-step').classList.add('running');
            document.getElementById('quantum-status').textContent = 'Executing Grover algorithm...';
            break;

        case 'workflow_completed':
            isAnalyzing = false;
            document.getElementById('analyze-btn').disabled = false;

            if (data.status === 'APPROVED') {
                updateVerdict('approved', '✅', 'MISSION APPROVED');
            } else if (data.status === 'REJECTED') {
                updateVerdict('rejected', '❌', 'MISSION REJECTED');
            } else if (data.status === 'NO_ACTION') {
                updateVerdict('approved', '🌍', 'NO ACTION NEEDED');
            }

            // Update quantum step
            document.getElementById('quantum-step').classList.remove('running');
            document.getElementById('quantum-step').classList.add('completed');
            document.getElementById('quantum-status').textContent = 'Complete';

            break;

        case 'workflow_error':
            isAnalyzing = false;
            document.getElementById('analyze-btn').disabled = false;
            updateVerdict('rejected', '⚠️', 'Error: ' + data.data.error);
            break;
    }
}

// ============================================================================
// FORM HANDLING
// ============================================================================

function initForm() {
    const form = document.getElementById('asteroid-form');

    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        if (isAnalyzing) return;

        const asteroidData = {
            name: document.getElementById('name').value,
            diameter_m: parseFloat(document.getElementById('diameter').value),
            mass_kg: parseFloat(document.getElementById('mass').value),
            velocity_km_s: parseFloat(document.getElementById('velocity').value),
            composition: document.getElementById('composition').value,
            impact_probability: parseFloat(document.getElementById('probability').value),
            days_until_approach: parseInt(document.getElementById('days').value)
        };

        await startAnalysis(asteroidData);
    });
}

function initDemoButtons() {
    document.querySelectorAll('.btn-demo').forEach(btn => {
        btn.addEventListener('click', () => {
            const demoKey = btn.dataset.demo;
            const data = demoAsteroids[demoKey];

            if (data) {
                document.getElementById('name').value = data.name;
                document.getElementById('diameter').value = data.diameter_m;
                document.getElementById('mass').value = data.mass_kg;
                document.getElementById('velocity').value = data.velocity_km_s;
                document.getElementById('composition').value = data.composition;
                document.getElementById('probability').value = data.impact_probability;
                document.getElementById('days').value = data.days_until_approach;
            }
        });
    });
}

async function startAnalysis(asteroidData) {
    if (!isConnected) {
        alert('Not connected to server. Please wait for connection.');
        return;
    }

    isAnalyzing = true;
    document.getElementById('analyze-btn').disabled = true;

    try {
        const response = await fetch(`${API_BASE}/analyze`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(asteroidData)
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const result = await response.json();
        console.log('[API] Analysis started:', result);

    } catch (error) {
        console.error('[API] Error:', error);
        alert('Failed to start analysis. Is the API server running?');
        isAnalyzing = false;
        document.getElementById('analyze-btn').disabled = false;
    }
}

// ============================================================================
// UI UPDATES
// ============================================================================

function showResults() {
    document.getElementById('results-placeholder').classList.add('hidden');
    document.getElementById('results-content').classList.remove('hidden');
}

function resetAgentSteps() {
    ['agent1', 'agent2', 'agent3', 'quantum'].forEach(agent => {
        const step = document.getElementById(`${agent}-step`);
        if (step) {
            step.classList.remove('running', 'completed');
        }
        const status = document.getElementById(`${agent}-status`);
        if (status) {
            status.textContent = 'Waiting...';
        }
        const result = document.getElementById(`${agent}-result`);
        if (result) {
            result.textContent = '';
        }
    });
}

function updateAgentStatus(agent, status, message) {
    let stepId;
    switch (agent) {
        case 'agent_1': stepId = 'agent1-step'; break;
        case 'agent_2': stepId = 'agent2-step'; break;
        case 'agent_3': stepId = 'agent3-step'; break;
        default: return;
    }

    const step = document.getElementById(stepId);
    const statusEl = document.getElementById(stepId.replace('-step', '-status'));

    if (step) {
        step.classList.remove('running', 'completed');
        step.classList.add(status);
    }

    if (statusEl) {
        statusEl.textContent = message;
    }
}

function updateAgentResult(agent, data) {
    let resultId;
    switch (agent) {
        case 'agent_1': resultId = 'agent1-result'; break;
        case 'agent_2': resultId = 'agent2-result'; break;
        case 'agent_3': resultId = 'agent3-result'; break;
        default: return;
    }

    const resultEl = document.getElementById(resultId);
    if (!resultEl) return;

    switch (agent) {
        case 'agent_1':
            resultEl.innerHTML = `Risk Score: <strong>${data.risk_score?.toFixed(1) || '-'}/10</strong> | ` +
                `Deflection: ${data.requires_deflection ? 'Required' : 'Not needed'}`;

            // Update threat card
            document.getElementById('risk-score').textContent = `${data.risk_score?.toFixed(1) || '-'}/10`;
            document.getElementById('kinetic-energy').textContent = `${data.kinetic_energy_mt?.toFixed(2) || '-'} MT`;
            document.getElementById('damage-category').textContent = data.kinetic_energy_mt > 1000 ? 'Global' : 'Regional';
            break;

        case 'agent_2':
            resultEl.innerHTML = `Optimal: Index ${data.optimal_index} | ` +
                `Velocity: ${data.optimal_velocity}km/s | ` +
                `Quantum: ${data.quantum_advantage?.toFixed(1) || '-'}x`;

            // Update quantum card
            document.getElementById('optimal-index').textContent = data.optimal_index;
            document.getElementById('quantum-advantage').textContent = `${data.quantum_advantage?.toFixed(1) || '-'}x`;
            document.getElementById('success-prob').textContent = `${(data.success_probability * 100)?.toFixed(1) || '-'}%`;
            document.getElementById('optimal-params').innerHTML =
                `<strong>Optimal Solution:</strong> Velocity ${data.optimal_velocity} km/s, ` +
                `Angle ${data.optimal_angle}°`;
            break;

        case 'agent_3':
            resultEl.innerHTML = `Verdict: <strong>${data.verdict}</strong> | ` +
                `Fragmentation: ${data.fragmentation_risk_pct?.toFixed(1)}%`;

            // Update safety card
            document.getElementById('frag-risk').textContent = `${data.fragmentation_risk_pct?.toFixed(1) || '-'}%`;
            document.getElementById('miss-distance').textContent = `${data.miss_distance_km?.toLocaleString() || '-'} km`;
            document.getElementById('confidence').textContent = `${data.confidence_score?.toFixed(1) || '-'}%`;
            break;
    }
}

function updateVerdict(type, icon, text) {
    const banner = document.getElementById('verdict-banner');
    banner.className = 'verdict-banner ' + type;

    document.getElementById('verdict-icon').textContent = icon;
    document.getElementById('verdict-text').textContent = text;
}
