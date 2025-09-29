"""
Configuration package for the AI Text Assistant Backend.
Provides centralized configuration management and environment variable loading.
"""

from .settings import Settings, settings
from .database import DatabaseManager, db_manager, get_database, get_collection
from .database_init import initialize_database, shutdown_database, database_lifespan, check_database_health
from .validation import validate_configuration, log_configuration_summary

__all__ = [
    "Settings", 
    "settings",
    "DatabaseManager",
    "db_manager",
    "get_database",
    "get_collection",
    "initialize_database",
    "shutdown_database", 
    "database_lifespan",
    "check_database_health",
    "validate_configuration",
    "log_configuration_summary"
]