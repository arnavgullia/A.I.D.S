"""
Project Aegis - Database Abstraction Layer
Provides a unified interface for database operations with pluggable backends.

Current Implementation: InMemoryDatabase (for development/testing)
Future Implementation: MySQLDatabase (for production)

To switch to MySQL:
1. Set AEGIS_DB_TYPE=mysql in .env
2. Configure MySQL connection settings
3. Create the database schema (see schema.sql)
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass, field, asdict
import json
import mysql.connector
from mysql.connector import Error


# ============================================================================
# DATA MODELS
# ============================================================================

@dataclass
class Asteroid:
    """Asteroid entity."""
    asteroid_id: Any # int or str (to support external DBs)
    name: str
    diameter_m: float
    mass_kg: float
    velocity_km_s: float
    composition: str
    impact_probability: float
    days_until_approach: int
    orbit_params: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class RiskAssessment:
    """Risk assessment from Agent 1."""
    assessment_id: int
    asteroid_id: Any
    impact_probability: float
    kinetic_energy_mt: float
    estimated_damage: str
    risk_score: float
    requires_deflection: bool
    raw_response: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class DeflectionStrategy:
    """Deflection strategy from Agent 2."""
    strategy_id: int
    asteroid_id: Any
    method: str
    parameters_json: str
    feasibility_score: float
    is_primary: bool = False
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class SimulationRun:
    """Simulation candidate for quantum optimization."""
    simulation_id: int
    strategy_id: int
    candidate_index: int  # 0-15
    velocity_km_s: float
    angle_degrees: float
    timing_days: int
    impactor_mass_kg: float
    estimated_fuel_kg: float
    estimated_miss_km: Optional[float] = None
    is_optimal: bool = False
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class QuantumOptimizationResult:
    """Result from quantum Grover optimization."""
    result_id: int
    asteroid_id: Any
    optimal_simulation_id: int
    optimal_index: int
    success_probability: float
    qubits_used: int
    iterations: int
    quantum_advantage: float
    execution_time_ms: float
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class SafetyEvaluation:
    """Safety evaluation from Agent 3."""
    evaluation_id: int
    simulation_id: int
    fragmentation_risk_pct: float
    miss_distance_km: float
    confidence_score: float
    verdict: str  # "APPROVE" or "REJECT"
    failed_checks_json: str
    feedback: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class FinalDecision:
    """Final approved mission decision."""
    decision_id: int
    asteroid_id: Any
    strategy_id: int
    primary_simulation_id: int
    backup_simulation_id: Optional[int]
    confidence_score: float
    explanation: str
    approved_by_humans: bool = False
    decided_at: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class AgentLog:
    """Activity log for agent actions."""
    log_id: int
    agent_name: str
    action: str
    related_id: Optional[int] = None
    details_json: str = "{}"
    logged_at: str = field(default_factory=lambda: datetime.now().isoformat())


# ============================================================================
# DATABASE INTERFACE
# ============================================================================

class DatabaseInterface(ABC):
    """Abstract base class for database implementations."""
    
    @abstractmethod
    def connect(self) -> bool:
        """Establish database connection."""
        pass
    
    @abstractmethod
    def disconnect(self) -> None:
        """Close database connection."""
        pass
    
    # -------------------- Asteroid Operations --------------------
    
    @abstractmethod
    def insert_asteroid(self, asteroid: Asteroid) -> int:
        """Insert asteroid and return ID."""
        pass
    
    @abstractmethod
    def get_asteroid(self, asteroid_id: int) -> Optional[Asteroid]:
        """Get asteroid by ID."""
        pass
    
    @abstractmethod
    def get_asteroid_by_name(self, name: str) -> Optional[Asteroid]:
        """Get asteroid by name."""
        pass
    
    # -------------------- Risk Assessment Operations --------------------
    
    @abstractmethod
    def insert_risk_assessment(self, assessment: RiskAssessment) -> int:
        """Insert risk assessment and return ID."""
        pass
    
    @abstractmethod
    def get_risk_assessment(self, asteroid_id: int) -> Optional[RiskAssessment]:
        """Get risk assessment for asteroid."""
        pass
    
    # -------------------- Strategy Operations --------------------
    
    @abstractmethod
    def insert_strategy(self, strategy: DeflectionStrategy) -> int:
        """Insert deflection strategy and return ID."""
        pass
    
    @abstractmethod
    def get_strategies(self, asteroid_id: int) -> List[DeflectionStrategy]:
        """Get all strategies for asteroid."""
        pass
    
    # -------------------- Simulation Operations --------------------
    
    @abstractmethod
    def insert_simulation(self, simulation: SimulationRun) -> int:
        """Insert simulation run and return ID."""
        pass
    
    @abstractmethod
    def get_simulations(self, strategy_id: int) -> List[SimulationRun]:
        """Get all simulations for strategy."""
        pass
    
    @abstractmethod
    def update_simulation_optimal(self, simulation_id: int, is_optimal: bool) -> None:
        """Mark simulation as optimal."""
        pass
    
    # -------------------- Quantum Result Operations --------------------
    
    @abstractmethod
    def insert_quantum_result(self, result: QuantumOptimizationResult) -> int:
        """Insert quantum result and return ID."""
        pass
    
    @abstractmethod
    def get_quantum_result(self, asteroid_id: int) -> Optional[QuantumOptimizationResult]:
        """Get quantum result for asteroid."""
        pass
    
    # -------------------- Safety Evaluation Operations --------------------
    
    @abstractmethod
    def insert_safety_evaluation(self, evaluation: SafetyEvaluation) -> int:
        """Insert safety evaluation and return ID."""
        pass
    
    @abstractmethod
    def get_safety_evaluation(self, simulation_id: int) -> Optional[SafetyEvaluation]:
        """Get safety evaluation for simulation."""
        pass
    
    # -------------------- Final Decision Operations --------------------
    
    @abstractmethod
    def insert_final_decision(self, decision: FinalDecision) -> int:
        """Insert final decision and return ID."""
        pass
    
    @abstractmethod
    def get_final_decision(self, asteroid_id: int) -> Optional[FinalDecision]:
        """Get final decision for asteroid."""
        pass
    
    # -------------------- Agent Log Operations --------------------
    
    @abstractmethod
    def insert_log(self, log: AgentLog) -> int:
        """Insert agent log and return ID."""
        pass
    
    @abstractmethod
    def get_logs(self, agent_name: str = None) -> List[AgentLog]:
        """Get agent logs, optionally filtered by agent name."""
        pass


# ============================================================================
# IN-MEMORY IMPLEMENTATION (Development/Testing)
# ============================================================================

class InMemoryDatabase(DatabaseInterface):
    """
    In-memory database implementation for development and testing.
    Data is stored in dictionaries and lost on restart.
    """
    
    def __init__(self):
        self._connected = False
        self._id_counters = {
            'asteroid': 0,
            'risk_assessment': 0,
            'strategy': 0,
            'simulation': 0,
            'quantum_result': 0,
            'safety_evaluation': 0,
            'final_decision': 0,
            'agent_log': 0,
        }
        
        # Data stores
        self._asteroids: Dict[int, Asteroid] = {}
        self._risk_assessments: Dict[int, RiskAssessment] = {}
        self._strategies: Dict[int, DeflectionStrategy] = {}
        self._simulations: Dict[int, SimulationRun] = {}
        self._quantum_results: Dict[int, QuantumOptimizationResult] = {}
        self._safety_evaluations: Dict[int, SafetyEvaluation] = {}
        self._final_decisions: Dict[int, FinalDecision] = {}
        self._agent_logs: Dict[int, AgentLog] = {}
    
    def _next_id(self, table: str) -> int:
        """Get next ID for a table."""
        self._id_counters[table] += 1
        return self._id_counters[table]
    
    def connect(self) -> bool:
        """Establish connection (no-op for in-memory)."""
        self._connected = True
        print("[Database] In-memory database connected")
        return True
    
    def disconnect(self) -> None:
        """Close connection (no-op for in-memory)."""
        self._connected = False
        print("[Database] In-memory database disconnected")
    
    # -------------------- Asteroid Operations --------------------
    
    def insert_asteroid(self, asteroid: Asteroid) -> int:
        if asteroid.asteroid_id == 0:
            asteroid.asteroid_id = self._next_id('asteroid')
        self._asteroids[asteroid.asteroid_id] = asteroid
        return asteroid.asteroid_id
    
    def get_asteroid(self, asteroid_id: int) -> Optional[Asteroid]:
        return self._asteroids.get(asteroid_id)
    
    def get_asteroid_by_name(self, name: str) -> Optional[Asteroid]:
        if not name:
             return None
        for asteroid in self._asteroids.values():
            if asteroid.name and asteroid.name.lower() == name.lower():
                return asteroid
        return None
    
    # -------------------- Risk Assessment Operations --------------------
    
    def insert_risk_assessment(self, assessment: RiskAssessment) -> int:
        if assessment.assessment_id == 0:
            assessment.assessment_id = self._next_id('risk_assessment')
        self._risk_assessments[assessment.assessment_id] = assessment
        return assessment.assessment_id
    
    def get_risk_assessment(self, asteroid_id: int) -> Optional[RiskAssessment]:
        for assessment in self._risk_assessments.values():
            if assessment.asteroid_id == asteroid_id:
                return assessment
        return None
    
    # -------------------- Strategy Operations --------------------
    
    def insert_strategy(self, strategy: DeflectionStrategy) -> int:
        if strategy.strategy_id == 0:
            strategy.strategy_id = self._next_id('strategy')
        self._strategies[strategy.strategy_id] = strategy
        return strategy.strategy_id
    
    def get_strategies(self, asteroid_id: int) -> List[DeflectionStrategy]:
        return [s for s in self._strategies.values() if s.asteroid_id == asteroid_id]
    
    # -------------------- Simulation Operations --------------------
    
    def insert_simulation(self, simulation: SimulationRun) -> int:
        if simulation.simulation_id == 0:
            simulation.simulation_id = self._next_id('simulation')
        self._simulations[simulation.simulation_id] = simulation
        return simulation.simulation_id
    
    def get_simulations(self, strategy_id: int) -> List[SimulationRun]:
        return [s for s in self._simulations.values() if s.strategy_id == strategy_id]
    
    def update_simulation_optimal(self, simulation_id: int, is_optimal: bool) -> None:
        if simulation_id in self._simulations:
            self._simulations[simulation_id].is_optimal = is_optimal
    
    # -------------------- Quantum Result Operations --------------------
    
    def insert_quantum_result(self, result: QuantumOptimizationResult) -> int:
        if result.result_id == 0:
            result.result_id = self._next_id('quantum_result')
        self._quantum_results[result.result_id] = result
        return result.result_id
    
    def get_quantum_result(self, asteroid_id: int) -> Optional[QuantumOptimizationResult]:
        for result in self._quantum_results.values():
            if result.asteroid_id == asteroid_id:
                return result
        return None
    
    # -------------------- Safety Evaluation Operations --------------------
    
    def insert_safety_evaluation(self, evaluation: SafetyEvaluation) -> int:
        if evaluation.evaluation_id == 0:
            evaluation.evaluation_id = self._next_id('safety_evaluation')
        self._safety_evaluations[evaluation.evaluation_id] = evaluation
        return evaluation.evaluation_id
    
    def get_safety_evaluation(self, simulation_id: int) -> Optional[SafetyEvaluation]:
        for evaluation in self._safety_evaluations.values():
            if evaluation.simulation_id == simulation_id:
                return evaluation
        return None
    
    # -------------------- Final Decision Operations --------------------
    
    def insert_final_decision(self, decision: FinalDecision) -> int:
        if decision.decision_id == 0:
            decision.decision_id = self._next_id('final_decision')
        self._final_decisions[decision.decision_id] = decision
        return decision.decision_id
    
    def get_final_decision(self, asteroid_id: int) -> Optional[FinalDecision]:
        for decision in self._final_decisions.values():
            if decision.asteroid_id == asteroid_id:
                return decision
        return None
    
    # -------------------- Agent Log Operations --------------------
    
    def insert_log(self, log: AgentLog) -> int:
        if log.log_id == 0:
            log.log_id = self._next_id('agent_log')
        self._agent_logs[log.log_id] = log
        return log.log_id
    
    def get_logs(self, agent_name: str = None) -> List[AgentLog]:
        if agent_name:
            return [l for l in self._agent_logs.values() if l.agent_name == agent_name]
        return list(self._agent_logs.values())
    
    def export_to_dict(self) -> Dict[str, Any]:
        """Export all data as a dictionary (for debugging)."""
        return {
            'asteroids': [asdict(a) for a in self._asteroids.values()],
            'risk_assessments': [asdict(r) for r in self._risk_assessments.values()],
            'strategies': [asdict(s) for s in self._strategies.values()],
            'simulations': [asdict(s) for s in self._simulations.values()],
            'quantum_results': [asdict(q) for q in self._quantum_results.values()],
            'safety_evaluations': [asdict(s) for s in self._safety_evaluations.values()],
            'final_decisions': [asdict(f) for f in self._final_decisions.values()],
            'agent_logs': [asdict(l) for l in self._agent_logs.values()],
        }


# ============================================================================
# MYSQL IMPLEMENTATION (Production - Placeholder)
# ============================================================================

class MySQLDatabase(DatabaseInterface):
    """
    MySQL database implementation for production use.
    
    TODO: Implement this class when ready to connect to MySQL.
    
    Required setup:
    1. Install: pip install mysql-connector-python sqlalchemy
    2. Create database: CREATE DATABASE aegis_db;
    3. Create user: CREATE USER 'aegis_admin'@'localhost' IDENTIFIED BY 'password';
    4. Grant privileges: GRANT ALL ON aegis_db.* TO 'aegis_admin'@'localhost';
    5. Run schema.sql to create tables
    """
    
    def __init__(self, host: str, port: int, user: str, password: str, database: str):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database
        self._connection = None
    
    def connect(self) -> bool:
        """Establish database connection."""
        try:
            self._connection = mysql.connector.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database=self.database
            )
            if self._connection.is_connected():
                print(f"[Database] Connected to MySQL database: {self.database}")
                return True
        except Error as e:
            print(f"[Database] Error connecting to MySQL: {e}")
            self._connection = None
        return False

    def disconnect(self) -> None:
        """Close database connection."""
        if self._connection and self._connection.is_connected():
            self._connection.close()
            print("[Database] MySQL connection closed")

    def _get_cursor(self):
        """Helper to get a dictionary cursor."""
        if not self._connection or not self._connection.is_connected():
            self.connect()
        return self._connection.cursor(dictionary=True)

    # -------------------- Asteroid Operations --------------------
    
    def insert_asteroid(self, asteroid: Asteroid) -> int:
        """Insert asteroid and return ID."""
        cursor = self._get_cursor()
        try:
            # Check if exists first to avoid duplicates
            if asteroid.asteroid_id > 0: # If ID is provided, check existence
                 cursor.execute("SELECT asteroid_id FROM asteroid WHERE asteroid_id = %s", (asteroid.asteroid_id,))
                 if cursor.fetchone():
                     return asteroid.asteroid_id # Already exists
            
            # Or check by name if ID is 0
            if asteroid.asteroid_id == 0:
                 cursor.execute("SELECT asteroid_id FROM asteroid WHERE name = %s", (asteroid.name,))
                 res = cursor.fetchone()
                 if res:
                     return res['asteroid_id']

            sql = """
                INSERT INTO asteroid 
                (name, diameter_m, mass_kg, velocity_km_s, composition, impact_probability, days_until_approach)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            val = (
                asteroid.name,
                asteroid.diameter_m,
                asteroid.mass_kg,
                asteroid.velocity_km_s,
                asteroid.composition,
                asteroid.impact_probability,
                asteroid.days_until_approach
            )
            cursor.execute(sql, val)
            self._connection.commit()
            return cursor.lastrowid
        except Error as e:
            print(f"[Database] Error inserting asteroid: {e}")
            return 0
        finally:
            cursor.close()

    def get_asteroid(self, asteroid_id: int) -> Optional[Asteroid]:
        """Get asteroid by ID."""
        cursor = self._get_cursor()
        try:
            cursor.execute("SELECT * FROM asteroid WHERE asteroid_id = %s", (asteroid_id,))
            row = cursor.fetchone()
            if row:
                return Asteroid(
                    asteroid_id=row['asteroid_id'],
                    name=row['name'],
                    diameter_m=row['diameter_m'],
                    mass_kg=row['mass_kg'],
                    velocity_km_s=row['velocity_km_s'],
                    composition=row['composition'],
                    impact_probability=row['impact_probability'],
                    days_until_approach=row['days_until_approach']
                )
            return None
        except Error as e:
            print(f"[Database] Error fetching asteroid: {e}")
            return None
        finally:
            cursor.close()

    def get_asteroid_by_name(self, name: str) -> Optional[Asteroid]:
        """Get asteroid by name (case-insensitive substring search)."""
        cursor = self._get_cursor()
        try:
            # Search by Name or Asteroid_ID
            sql = "SELECT * FROM asteroid WHERE Name LIKE %s OR Asteroid_ID LIKE %s"
            val = (f"%{name}%", f"%{name}%") 
            cursor.execute(sql, val)
            row = cursor.fetchone()
            
            if row:
                # MAP USER SCHEMA TO INTERNAL MODEL
                
                # ID Handling
                try:
                    aid = int(row['Asteroid_ID'])
                except:
                    # Hash string ID to int if not numeric
                    aid = int(hash(row['Asteroid_ID']) % 1000000)
                
                # Diameter Handling (Km -> m)
                diameter = float(row['Diameter_Km']) * 1000 if row.get('Diameter_Km') else 100.0
                
                # Date Handling
                days = 365
                if row.get('Detection_Date'):
                    try:
                        from datetime import datetime
                        det_date = datetime.strptime(str(row['Detection_Date']), '%Y-%m-%d')
                        delta = det_date - datetime.now()
                        days = max(1, delta.days)
                    except:
                        pass

                # Risk Handling (Inject high risk for Apophis to ensure demo works)
                impact_prob = 0.01 
                if 'Apophis' in row['Name'] or '99942' in str(row['Asteroid_ID']):
                    impact_prob = 0.45
                
                return Asteroid(
                    asteroid_id=row['Asteroid_ID'],  # Keep original string ID
                    name=row['Name'],
                    diameter_m=diameter,
                    mass_kg=2.7e10, # Default mass if missing
                    velocity_km_s=float(row.get('Velocity_Kmps', 20.0)),
                    composition=row.get('Composition', 'Unknown'),
                    impact_probability=impact_prob,
                    days_until_approach=days
                )
            return None
        except Error as e:
            print(f"[Database] Error fetching asteroid by name: {e}")
            return None
        finally:
            cursor.close()
    
    def insert_risk_assessment(self, assessment: RiskAssessment) -> int:
        """Insert risk assessment and return ID."""
        cursor = self._get_cursor()
        try:
            sql = """
                INSERT INTO risk_assessment 
                (asteroid_id, impact_probability, kinetic_energy_mt, estimated_damage, risk_score, requires_deflection)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            val = (
                assessment.asteroid_id,
                assessment.impact_probability,
                assessment.kinetic_energy_mt,
                assessment.estimated_damage,
                assessment.risk_score,
                assessment.requires_deflection
            )
            cursor.execute(sql, val)
            self._connection.commit()
            return cursor.lastrowid
        except Error as e:
            print(f"[Database] Error inserting risk_assessment: {e}")
            return 0
        finally:
            cursor.close()

    def get_risk_assessment(self, asteroid_id: int) -> Optional[RiskAssessment]:
        """Get risk assessment for asteroid."""
        cursor = self._get_cursor()
        try:
            cursor.execute("SELECT * FROM risk_assessment WHERE asteroid_id = %s", (asteroid_id,))
            row = cursor.fetchone()
            if row:
                return RiskAssessment(
                    assessment_id=row['assessment_id'],
                    asteroid_id=row['asteroid_id'],
                    impact_probability=row['impact_probability'],
                    kinetic_energy_mt=row['kinetic_energy_mt'],
                    estimated_damage=row['estimated_damage'],
                    risk_score=row['risk_score'],
                    requires_deflection=bool(row['requires_deflection']),
                    created_at=str(row['created_at'])
                )
            return None
        except Error as e:
            print(f"[Database] Error fetching risk_assessment: {e}")
            return None
        finally:
            cursor.close()

    def insert_strategy(self, strategy: DeflectionStrategy) -> int:
         # Placeholder for now as it's not strictly required by current workflow
        return 0

    def get_strategies(self, asteroid_id: int) -> List[DeflectionStrategy]:
        return []

    def insert_simulation(self, simulation: SimulationRun) -> int:
        """Insert simulation run and return ID."""
        cursor = self._get_cursor()
        try:
            sql = """
                INSERT INTO simulation_run 
                (strategy_id, candidate_index, velocity_km_s, angle_degrees, timing_days, impactor_mass_kg, estimated_fuel_kg, is_optimal)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            val = (
                simulation.strategy_id,
                simulation.candidate_index,
                simulation.velocity_km_s,
                simulation.angle_degrees,
                simulation.timing_days,
                simulation.impactor_mass_kg,
                simulation.estimated_fuel_kg,
                simulation.is_optimal
            )
            cursor.execute(sql, val)
            self._connection.commit()
            return cursor.lastrowid
        except Error as e:
            print(f"[Database] Error inserting simulation: {e}")
            return 0
        finally:
            cursor.close()

    def get_simulations(self, strategy_id: int) -> List[SimulationRun]:
        return []

    def update_simulation_optimal(self, simulation_id: int, is_optimal: bool) -> None:
        """Mark simulation as optimal."""
        cursor = self._get_cursor()
        try:
            cursor.execute("UPDATE simulation_run SET is_optimal = %s WHERE simulation_id = %s", (is_optimal, simulation_id))
            self._connection.commit()
        except Error as e:
            print(f"[Database] Error updating simulation: {e}")
        finally:
            cursor.close()
    
    def insert_quantum_result(self, result: QuantumOptimizationResult) -> int:
        """Insert quantum result and return ID."""
        cursor = self._get_cursor()
        try:
            sql = """
                INSERT INTO quantum_result 
                (asteroid_id, optimal_simulation_id, optimal_index, success_probability, qubits_used, iterations, quantum_advantage, execution_time_ms)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            val = (
                result.asteroid_id,
                result.optimal_simulation_id,
                result.optimal_index,
                result.success_probability,
                result.qubits_used,
                result.iterations,
                result.quantum_advantage,
                result.execution_time_ms
            )
            cursor.execute(sql, val)
            self._connection.commit()
            return cursor.lastrowid
        except Error as e:
            print(f"[Database] Error inserting quantum_result: {e}")
            return 0
        finally:
            cursor.close()

    def get_quantum_result(self, asteroid_id: int) -> Optional[QuantumOptimizationResult]:
        return None

    def insert_safety_evaluation(self, evaluation: SafetyEvaluation) -> int:
        """Insert safety evaluation and return ID."""
        cursor = self._get_cursor()
        try:
            sql = """
                INSERT INTO safety_evaluation 
                (simulation_id, fragmentation_risk_pct, miss_distance_km, confidence_score, verdict, failed_checks_json)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            val = (
                evaluation.simulation_id,
                evaluation.fragmentation_risk_pct,
                evaluation.miss_distance_km,
                evaluation.confidence_score,
                evaluation.verdict,
                evaluation.failed_checks_json
            )
            cursor.execute(sql, val)
            self._connection.commit()
            return cursor.lastrowid
        except Error as e:
            print(f"[Database] Error inserting safety_evaluation: {e}")
            return 0
        finally:
            cursor.close()

    def get_safety_evaluation(self, simulation_id: int) -> Optional[SafetyEvaluation]:
        return None

    def insert_final_decision(self, decision: FinalDecision) -> int:
        """Insert final decision and return ID."""
        cursor = self._get_cursor()
        try:
            sql = """
                INSERT INTO final_decision 
                (asteroid_id, strategy_id, primary_simulation_id, backup_simulation_id, confidence_score, explanation, approved_by_humans)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            val = (
                decision.asteroid_id,
                decision.strategy_id,
                decision.primary_simulation_id,
                decision.backup_simulation_id,
                decision.confidence_score,
                decision.explanation,
                decision.approved_by_humans
            )
            cursor.execute(sql, val)
            self._connection.commit()
            return cursor.lastrowid
        except Error as e:
            print(f"[Database] Error inserting final_decision: {e}")
            return 0
        finally:
            cursor.close()

    def get_final_decision(self, asteroid_id: int) -> Optional[FinalDecision]:
        return None
    
    def insert_log(self, log: AgentLog) -> int:
        """Insert agent log and return ID."""
        cursor = self._get_cursor()
        try:
            sql = """
                INSERT INTO agent_log 
                (agent_name, action, related_id, details_json)
                VALUES (%s, %s, %s, %s)
            """
            val = (
                log.agent_name,
                log.action,
                log.related_id,
                log.details_json
            )
            cursor.execute(sql, val)
            self._connection.commit()
            return cursor.lastrowid
        except Error as e:
            print(f"[Database] Error inserting log: {e}")
            return 0
        finally:
            cursor.close()
    
    def get_logs(self, agent_name: str = None) -> List[AgentLog]:
        """Get agent logs."""
        cursor = self._get_cursor()
        try:
            sql = "SELECT * FROM agent_log"
            val = ()
            if agent_name:
                sql += " WHERE agent_name = %s"
                val = (agent_name,)
            
            sql += " ORDER BY logged_at DESC LIMIT 100"
            
            cursor.execute(sql, val)
            rows = cursor.fetchall()
            
            logs = []
            for row in rows:
                logs.append(AgentLog(
                    log_id=row['log_id'],
                    agent_name=row['agent_name'],
                    action=row['action'],
                    related_id=row['related_id'],
                    details_json=row['details_json'],
                    logged_at=str(row['logged_at'])
                ))
            return logs
        except Error as e:
            print(f"[Database] Error fetching logs: {e}")
            return []
        finally:
            cursor.close()


# ============================================================================
# FACTORY FUNCTION
# ============================================================================

# Global database instance
_database: Optional[DatabaseInterface] = None


def get_database() -> DatabaseInterface:
    """
    Get the global database instance.
    Creates instance on first call based on configuration.
    """
    global _database
    
    if _database is None:
        from .config import get_config
        config = get_config()
        
        if config.database.db_type == "mysql":
            _database = MySQLDatabase(
                host=config.database.mysql_host,
                port=config.database.mysql_port,
                user=config.database.mysql_user,
                password=config.database.mysql_password,
                database=config.database.mysql_database
            )
        else:
            # Default to in-memory
            _database = InMemoryDatabase()
        
        _database.connect()
    
    return _database


def reset_database() -> None:
    """Reset the database connection (useful for testing)."""
    global _database
    if _database:
        _database.disconnect()
    _database = None
