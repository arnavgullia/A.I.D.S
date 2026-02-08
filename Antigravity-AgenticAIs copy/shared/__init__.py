"""
Project Aegis - Shared Infrastructure Module
Contains state management, database abstraction, and quantum integration.
"""

from .state_schema import AegisState, create_initial_state
from .database import get_database, DatabaseInterface
from .config import Config

__all__ = [
    'AegisState',
    'create_initial_state', 
    'get_database',
    'DatabaseInterface',
    'Config'
]
