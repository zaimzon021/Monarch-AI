"""
Database initialization and lifecycle management.
"""

import asyncio
from contextlib import asynccontextmanager
from typing import Dict, Any
import structlog

from .database import db_manager
from .settings import settings

logger = structlog.get_logger(__name__)


async def initialize_database() -> bool:
    """
    Initialize database connection.
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        logger.info("Initializing database connection")
        
        # Connect to database with retry logic
        success = await db_manager.connect_with_retry()
        
        if success:
            logger.info("Database initialized successfully")
            return True
        else:
            logger.error("Failed to initialize database")
            return False
            
    except Exception as e:
        logger.error(f"Database initialization error: {str(e)}")
        return False


async def shutdown_database():
    """Shutdown database connection."""
    try:
        logger.info("Shutting down database connection")
        await db_manager.disconnect()
        logger.info("Database shutdown completed")
    except Exception as e:
        logger.error(f"Database shutdown error: {str(e)}")


async def check_database_health() -> Dict[str, Any]:
    """
    Check database health status.
    
    Returns:
        Dict containing health status information
    """
    try:
        return await db_manager.health_check()
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "connected": False
        }


@asynccontextmanager
async def database_lifespan(app):
    """
    Database lifespan context manager for FastAPI.
    
    Args:
        app: FastAPI application instance
    """
    # Startup
    logger.info("Starting database lifespan")
    
    success = await initialize_database()
    if not success:
        logger.critical("Failed to initialize database - application cannot start")
        raise RuntimeError("Database initialization failed")
    
    try:
        yield
    finally:
        # Shutdown
        logger.info("Ending database lifespan")
        await shutdown_database()


async def create_indexes():
    """Create database indexes for optimal performance."""
    try:
        if not db_manager.is_connected:
            logger.warning("Database not connected, skipping index creation")
            return
        
        logger.info("Creating database indexes")
        
        # Get collections
        modifications_collection = db_manager.get_collection("modification_records")
        sessions_collection = db_manager.get_collection("user_sessions")
        metrics_collection = db_manager.get_collection("system_metrics")
        
        # Create indexes for modification_records
        await modifications_collection.create_index("user_id")
        await modifications_collection.create_index("timestamp")
        await modifications_collection.create_index("operation")
        await modifications_collection.create_index([("user_id", 1), ("timestamp", -1)])
        
        # Create indexes for user_sessions
        await sessions_collection.create_index("user_id")
        await sessions_collection.create_index("session_start")
        
        # Create indexes for system_metrics
        await metrics_collection.create_index("timestamp")
        
        logger.info("Database indexes created successfully")
        
    except Exception as e:
        logger.error(f"Failed to create database indexes: {str(e)}")


async def cleanup_old_records():
    """Clean up old records to manage database size."""
    try:
        if not db_manager.is_connected:
            logger.warning("Database not connected, skipping cleanup")
            return
        
        logger.info("Starting database cleanup")
        
        from datetime import datetime, timedelta
        
        # Clean up old system metrics (keep last 30 days)
        cutoff_date = datetime.utcnow() - timedelta(days=30)
        
        metrics_collection = db_manager.get_collection("system_metrics")
        result = await metrics_collection.delete_many({
            "timestamp": {"$lt": cutoff_date}
        })
        
        logger.info(f"Cleaned up {result.deleted_count} old metric records")
        
        # Clean up old user sessions (keep last 90 days)
        session_cutoff = datetime.utcnow() - timedelta(days=90)
        
        sessions_collection = db_manager.get_collection("user_sessions")
        result = await sessions_collection.delete_many({
            "session_start": {"$lt": session_cutoff}
        })
        
        logger.info(f"Cleaned up {result.deleted_count} old session records")
        
    except Exception as e:
        logger.error(f"Database cleanup failed: {str(e)}")