-- Project Aegis - MySQL Database Schema
-- Run this script to create all required tables for production use.
--
-- Usage:
-- 1. Create database: CREATE DATABASE aegis_db;
-- 2. Create user: CREATE USER 'aegis_admin'@'localhost' IDENTIFIED BY 'your_password';
-- 3. Grant privileges: GRANT ALL ON aegis_db.* TO 'aegis_admin'@'localhost';
-- 4. Run this script: mysql -u aegis_admin -p aegis_db < schema.sql

USE aegis_db;

-- ============================================================================
-- CORE TABLES
-- ============================================================================

-- Asteroid table: Stores input asteroid data
CREATE TABLE IF NOT EXISTS asteroid (
    asteroid_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    diameter_m DOUBLE NOT NULL,
    mass_kg DOUBLE NOT NULL,
    velocity_km_s DOUBLE NOT NULL,
    composition VARCHAR(100) NOT NULL,
    impact_probability DOUBLE NOT NULL,
    days_until_approach INT NOT NULL,
    orbit_params_json TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_name (name),
    INDEX idx_impact_probability (impact_probability)
);

-- Risk Assessment table: Agent 1 output
CREATE TABLE IF NOT EXISTS risk_assessment (
    assessment_id INT PRIMARY KEY AUTO_INCREMENT,
    asteroid_id INT NOT NULL,
    impact_probability DOUBLE NOT NULL,
    kinetic_energy_mt DOUBLE NOT NULL,
    estimated_damage VARCHAR(50) NOT NULL,
    risk_score DOUBLE NOT NULL,
    requires_deflection BOOLEAN NOT NULL,
    raw_response TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (asteroid_id) REFERENCES asteroid(asteroid_id) ON DELETE CASCADE,
    INDEX idx_asteroid (asteroid_id),
    INDEX idx_risk_score (risk_score)
);

-- Deflection Strategy table: Agent 2 strategies
CREATE TABLE IF NOT EXISTS deflection_strategy (
    strategy_id INT PRIMARY KEY AUTO_INCREMENT,
    asteroid_id INT NOT NULL,
    method VARCHAR(100) NOT NULL,
    parameters_json TEXT NOT NULL,
    feasibility_score DOUBLE NOT NULL,
    is_primary BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (asteroid_id) REFERENCES asteroid(asteroid_id) ON DELETE CASCADE,
    INDEX idx_asteroid (asteroid_id),
    INDEX idx_method (method)
);

-- Simulation Run table: 16 candidates for quantum optimization
CREATE TABLE IF NOT EXISTS simulation_run (
    simulation_id INT PRIMARY KEY AUTO_INCREMENT,
    strategy_id INT NOT NULL,
    candidate_index INT NOT NULL,  -- 0-15 for quantum encoding
    velocity_km_s DOUBLE NOT NULL,
    angle_degrees DOUBLE NOT NULL,
    timing_days INT NOT NULL,
    impactor_mass_kg DOUBLE NOT NULL,
    estimated_fuel_kg DOUBLE,
    estimated_miss_km DOUBLE,
    is_optimal BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (strategy_id) REFERENCES deflection_strategy(strategy_id) ON DELETE CASCADE,
    INDEX idx_strategy (strategy_id),
    INDEX idx_optimal (is_optimal)
);

-- Quantum Optimization Result table
CREATE TABLE IF NOT EXISTS quantum_optimization_result (
    result_id INT PRIMARY KEY AUTO_INCREMENT,
    asteroid_id INT NOT NULL,
    optimal_simulation_id INT NOT NULL,
    optimal_index INT NOT NULL,  -- 0-15
    success_probability DOUBLE NOT NULL,
    qubits_used INT NOT NULL,
    iterations INT NOT NULL,
    quantum_advantage DOUBLE NOT NULL,
    execution_time_ms DOUBLE NOT NULL,
    measurement_counts_json TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (asteroid_id) REFERENCES asteroid(asteroid_id) ON DELETE CASCADE,
    FOREIGN KEY (optimal_simulation_id) REFERENCES simulation_run(simulation_id),
    INDEX idx_asteroid (asteroid_id)
);

-- Safety Evaluation table: Agent 3 output
CREATE TABLE IF NOT EXISTS safety_evaluation (
    evaluation_id INT PRIMARY KEY AUTO_INCREMENT,
    simulation_id INT NOT NULL,
    fragmentation_risk_pct DOUBLE NOT NULL,
    miss_distance_km DOUBLE NOT NULL,
    confidence_score DOUBLE NOT NULL,
    verdict VARCHAR(20) NOT NULL,  -- APPROVE or REJECT
    failed_checks_json TEXT,
    feedback TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (simulation_id) REFERENCES simulation_run(simulation_id) ON DELETE CASCADE,
    INDEX idx_simulation (simulation_id),
    INDEX idx_verdict (verdict)
);

-- Final Decision table: Approved missions
CREATE TABLE IF NOT EXISTS final_decision (
    decision_id INT PRIMARY KEY AUTO_INCREMENT,
    asteroid_id INT NOT NULL,
    strategy_id INT NOT NULL,
    primary_simulation_id INT NOT NULL,
    backup_simulation_id INT,
    confidence_score DOUBLE NOT NULL,
    explanation TEXT NOT NULL,
    approved_by_humans BOOLEAN DEFAULT FALSE,
    decided_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    human_approval_at TIMESTAMP,
    
    FOREIGN KEY (asteroid_id) REFERENCES asteroid(asteroid_id) ON DELETE CASCADE,
    FOREIGN KEY (strategy_id) REFERENCES deflection_strategy(strategy_id),
    FOREIGN KEY (primary_simulation_id) REFERENCES simulation_run(simulation_id),
    FOREIGN KEY (backup_simulation_id) REFERENCES simulation_run(simulation_id),
    INDEX idx_asteroid (asteroid_id),
    INDEX idx_approved (approved_by_humans)
);

-- Agent Log table: Activity logging
CREATE TABLE IF NOT EXISTS agent_log (
    log_id INT PRIMARY KEY AUTO_INCREMENT,
    agent_name VARCHAR(50) NOT NULL,
    action VARCHAR(100) NOT NULL,
    related_id INT,
    details_json TEXT,
    logged_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_agent (agent_name),
    INDEX idx_action (action),
    INDEX idx_logged_at (logged_at)
);

-- ============================================================================
-- VIEWS FOR COMMON QUERIES
-- ============================================================================

-- Complete mission overview
CREATE OR REPLACE VIEW mission_overview AS
SELECT 
    a.asteroid_id,
    a.name AS asteroid_name,
    a.diameter_m,
    a.impact_probability,
    ra.risk_score,
    ra.requires_deflection,
    ds.method AS deflection_method,
    qor.optimal_index,
    qor.quantum_advantage,
    se.verdict AS safety_verdict,
    fd.approved_by_humans,
    fd.decided_at
FROM asteroid a
LEFT JOIN risk_assessment ra ON a.asteroid_id = ra.asteroid_id
LEFT JOIN deflection_strategy ds ON a.asteroid_id = ds.asteroid_id AND ds.is_primary = TRUE
LEFT JOIN quantum_optimization_result qor ON a.asteroid_id = qor.asteroid_id
LEFT JOIN simulation_run sr ON qor.optimal_simulation_id = sr.simulation_id
LEFT JOIN safety_evaluation se ON sr.simulation_id = se.simulation_id
LEFT JOIN final_decision fd ON a.asteroid_id = fd.asteroid_id;

-- Agent activity summary
CREATE OR REPLACE VIEW agent_activity_summary AS
SELECT 
    agent_name,
    action,
    COUNT(*) as action_count,
    MAX(logged_at) as last_occurrence
FROM agent_log
GROUP BY agent_name, action
ORDER BY agent_name, action_count DESC;

-- ============================================================================
-- SAMPLE DATA FOR TESTING
-- ============================================================================

INSERT INTO asteroid (name, diameter_m, mass_kg, velocity_km_s, composition, impact_probability, days_until_approach)
VALUES 
    ('Apophis-99942', 340, 2.7e10, 30.0, 'Stony-Iron', 0.02, 1000),
    ('Bennu-101955', 500, 7.3e10, 28.0, 'Rubble Pile', 0.05, 36500),
    ('Small-Rock-001', 30, 1e7, 15.0, 'Stony', 0.001, 3650);

-- ============================================================================
-- STORED PROCEDURES
-- ============================================================================

DELIMITER //

-- Get complete analysis for an asteroid
CREATE PROCEDURE get_asteroid_analysis(IN p_asteroid_id INT)
BEGIN
    -- Asteroid info
    SELECT * FROM asteroid WHERE asteroid_id = p_asteroid_id;
    
    -- Risk assessment
    SELECT * FROM risk_assessment WHERE asteroid_id = p_asteroid_id;
    
    -- Strategies
    SELECT * FROM deflection_strategy WHERE asteroid_id = p_asteroid_id;
    
    -- Quantum result
    SELECT * FROM quantum_optimization_result WHERE asteroid_id = p_asteroid_id;
    
    -- Final decision
    SELECT * FROM final_decision WHERE asteroid_id = p_asteroid_id;
    
    -- Agent logs
    SELECT * FROM agent_log WHERE related_id = p_asteroid_id ORDER BY logged_at;
END //

DELIMITER ;
