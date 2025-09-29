"""
MongoDB database connection and configuration.
Uses motor for async MongoDB operations.
"""

import asyncio
import logging
from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from .settings import settings

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manages MongoDB database connections and operations."""
    
    def __init__(self):
        self.client: Optional[AsyncIOMotorClient] = None
        self.database: Optional[AsyncIOMotorDatabase] = None
        self._connection_retries = 3
        self._retry_delay = 5  # seconds
    
    async def connect(self) -> bool:
        """
        Establish connection to MongoDB database.
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            logger.info(f"Connecting to MongoDB at {settings.mongodb_url}")
            
            # Create MongoDB client with connection options
            self.client = AsyncIOMotorClient(
                settings.mongodb_url,
                serverSelectionTimeoutMS=5000,  # 5 second timeout
                connectTimeoutMS=10000,         # 10 second connection timeout
                socketTimeoutMS=20000,          # 20 second socket timeout
                maxPoolSize=10,                 # Maximum connection pool size
                minPoolSize=1,                  # Minimum connection pool size
                retryWrites=True,               # Enable retryable writes
                retryReads=True                 # Enable retryable reads
            )
            
            # Get database instance
            self.database = self.client[settings.mongodb_database]
            
            # Test the connection
            await self._test_connection()
            
            logger.info(f"Successfully connected to MongoDB database: {settings.mongodb_database}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {str(e)}")
            await self.disconnect()
            return False
    
    async def connect_with_retry(self) -> bool:
        """
        Connect to MongoDB with retry logic.
        
        Returns:
            bool: True if connection successful after retries, False otherwise
        """
        for attempt in range(1, self._connection_retries + 1):
            logger.info(f"MongoDB connection attempt {attempt}/{self._connection_retries}")
            
            if await self.connect():
                return True
            
            if attempt < self._connection_retries:
                logger.warning(f"Connection failed, retrying in {self._retry_delay} seconds...")
                await asyncio.sleep(self._retry_delay)
            else:
                logger.error("All connection attempts failed")
        
        return False
    
    async def disconnect(self):
        """Close the MongoDB connection."""
        if self.client:
            try:
                self.client.close()
                logger.info("MongoDB connection closed")
            except Exception as e:
                logger.error(f"Error closing MongoDB connection: {str(e)}")
            finally:
                self.client = None
                self.database = None
    
    async def _test_connection(self):
        """Test the MongoDB connection by pinging the server."""
        if not self.client:
            raise ConnectionFailure("No MongoDB client available")
        
        try:
            # Ping the server to test connection
            await self.client.admin.command('ping')
            logger.debug("MongoDB ping successful")
        except Exception as e:
            logger.error(f"MongoDB ping failed: {str(e)}")
            raise
    
    async def health_check(self) -> dict:
        """
        Perform a health check on the database connection.
        
        Returns:
            dict: Health check results
        """
        health_status = {
            "status": "unhealthy",
            "database": settings.mongodb_database,
            "connected": False,
            "error": None
        }
        
        try:
            if not self.client or not self.database:
                health_status["error"] = "No database connection"
                return health_status
            
            # Test connection with ping
            await self.client.admin.command('ping')
            
            # Get server info
            server_info = await self.client.server_info()
            
            health_status.update({
                "status": "healthy",
                "connected": True,
                "server_version": server_info.get("version"),
                "max_bson_size": server_info.get("maxBsonObjectSize"),
                "max_message_size": server_info.get("maxMessageSizeBytes")
            })
            
        except ConnectionFailure as e:
            health_status["error"] = f"Connection failure: {str(e)}"
            logger.warning(f"Database health check failed: {str(e)}")
        except ServerSelectionTimeoutError as e:
            health_status["error"] = f"Server selection timeout: {str(e)}"
            logger.warning(f"Database health check failed: {str(e)}")
        except Exception as e:
            health_status["error"] = f"Unexpected error: {str(e)}"
            logger.error(f"Database health check failed: {str(e)}")
        
        return health_status
    
    def get_collection(self, collection_name: str):
        """
        Get a collection from the database.
        
        Args:
            collection_name: Name of the collection
            
        Returns:
            AsyncIOMotorCollection: The requested collection
            
        Raises:
            RuntimeError: If database is not connected
        """
        if not self.database:
            raise RuntimeError("Database not connected. Call connect() first.")
        
        return self.database[collection_name]
    
    @property
    def is_connected(self) -> bool:
        """Check if database is connected."""
        return self.client is not None and self.database is not None


# Global database manager instance
db_manager = DatabaseManager()


async def get_database() -> AsyncIOMotorDatabase:
    """
    Dependency function to get the database instance.
    
    Returns:
        AsyncIOMotorDatabase: The database instance
        
    Raises:
        RuntimeError: If database is not connected
    """
    if not db_manager.database:
        raise RuntimeError("Database not connected")
    
    return db_manager.database


async def get_collection(collection_name: str):
    """
    Dependency function to get a specific collection.
    
    Args:
        collection_name: Name of the collection
        
    Returns:
        AsyncIOMotorCollection: The requested collection
    """
    return db_manager.get_collection(collection_name)