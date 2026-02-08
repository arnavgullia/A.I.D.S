"""
Project Aegis - Configuration Module
Central configuration for all agents and shared infrastructure.
"""

import os
from dataclasses import dataclass, field
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


@dataclass
class DatabaseConfig:
    """Database configuration settings."""
    # Database type: "memory" (default) or "mysql" (future)
    db_type: str = "memory"
    
    # MySQL settings (placeholders for future connection)
    mysql_host: str = "localhost"
    mysql_port: int = 3306
    mysql_user: str = "aegis_admin"
    mysql_password: str = ""
    mysql_database: str = "aegis_db"
    
    @classmethod
    def from_env(cls) -> 'DatabaseConfig':
        """Load database config from environment variables."""
        return cls(
            db_type=os.getenv("AEGIS_DB_TYPE", "memory"),
            mysql_host=os.getenv("AEGIS_MYSQL_HOST", "localhost"),
            mysql_port=int(os.getenv("AEGIS_MYSQL_PORT", "3306")),
            mysql_user=os.getenv("AEGIS_MYSQL_USER", "aegis_admin"),
            mysql_password=os.getenv("AEGIS_MYSQL_PASSWORD", ""),
            mysql_database=os.getenv("AEGIS_MYSQL_DATABASE", "aegis_db"),
        )


@dataclass
class QuantumConfig:
    """Quantum module configuration."""
    # Path to the quantum module
    quantum_module_path: str = "/home/pranjay/workspace/A.I.D.S/Quantum_Grover"
    
    # Grover algorithm settings
    num_candidates: int = 16  # 4 qubits = 16 candidates
    shots: int = 2048  # Quantum measurement shots
    
    @classmethod
    def from_env(cls) -> 'QuantumConfig':
        """Load quantum config from environment variables."""
        return cls(
            quantum_module_path=os.getenv(
                "AEGIS_QUANTUM_PATH", 
                "/home/pranjay/workspace/A.I.D.S/Quantum_Grover"
            ),
            num_candidates=int(os.getenv("AEGIS_QUANTUM_CANDIDATES", "16")),
            shots=int(os.getenv("AEGIS_QUANTUM_SHOTS", "2048")),
        )


@dataclass
class AgentConfig:
    """Configuration for AI agents."""
    # Google API keys for each agent
    agent1_api_key: Optional[str] = None
    agent2_api_key: Optional[str] = None
    agent3_api_key: Optional[str] = None
    
    # Default model to use
    default_model: str = "gemini-2.5-flash-lite"
    
    # Agent-specific paths
    agent1_path: str = ""
    agent2_path: str = ""
    agent3_path: str = ""
    
    @classmethod
    def from_env(cls, base_path: str = "") -> 'AgentConfig':
        """Load agent config from environment variables."""
        # Try agent-specific keys first, then fall back to generic key
        generic_key = os.getenv("GOOGLE_API_KEY")
        
        return cls(
            agent1_api_key=os.getenv("AGENT1_GOOGLE_API_KEY") or generic_key,
            agent2_api_key=os.getenv("AGENT2_GOOGLE_API_KEY") or generic_key,
            agent3_api_key=os.getenv("AGENT3_GOOGLE_API_KEY") or generic_key,
            default_model=os.getenv("AEGIS_DEFAULT_MODEL", "gemini-2.5-flash-lite"),
            agent1_path=os.path.join(base_path, "Agent-1") if base_path else "",
            agent2_path=os.path.join(base_path, "Agent-2") if base_path else "",
            agent3_path=os.path.join(base_path, "Agent-3") if base_path else "",
        )


@dataclass
class Config:
    """Main configuration class for Project Aegis."""
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    quantum: QuantumConfig = field(default_factory=QuantumConfig)
    agents: AgentConfig = field(default_factory=AgentConfig)
    
    # Workflow settings
    max_iterations: int = 3  # Max Agent 3 rejection loops
    risk_threshold: float = 4.0  # Minimum risk score to activate deflection
    
    # Base path for the project
    base_path: str = ""
    
    @classmethod
    def load(cls, base_path: str = "") -> 'Config':
        """Load complete configuration from environment."""
        if not base_path:
            base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        return cls(
            database=DatabaseConfig.from_env(),
            quantum=QuantumConfig.from_env(),
            agents=AgentConfig.from_env(base_path),
            max_iterations=int(os.getenv("AEGIS_MAX_ITERATIONS", "3")),
            risk_threshold=float(os.getenv("AEGIS_RISK_THRESHOLD", "4.0")),
            base_path=base_path,
        )


# Global config instance (lazy loaded)
_config: Optional[Config] = None


def get_config() -> Config:
    """Get the global configuration instance."""
    global _config
    if _config is None:
        _config = Config.load()
    return _config


def reload_config(base_path: str = "") -> Config:
    """Reload configuration from environment."""
    global _config
    _config = Config.load(base_path)
    return _config
