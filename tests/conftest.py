"""
Pytest configuration and fixtures for testing.
"""

import asyncio
import pytest
from typing import AsyncGenerator
from fastapi.testclient import TestClient
from motor.motor_asyncio import AsyncIOMotorClient

from app.main import app
from app.config.settings import settings
from app.config.database import db_manager
from app.services.ai_service import ai_service_instance


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def client():
    """Create test client for FastAPI app."""
    return TestClient(app)


@pytest.fixture
async def test_db():
    """Create test database connection."""
    # Use test database
    test_db_url = "mongodb://localhost:27017/test_ai_text_assistant"
    
    # Create test client
    test_client = AsyncIOMotorClient(test_db_url)
    test_database = test_client["test_ai_text_assistant"]
    
    yield test_database
    
    # Cleanup: drop test database
    await test_client.drop_database("test_ai_text_assistant")
    test_client.close()


@pytest.fixture
async def mock_ai_service():
    """Mock AI service for testing."""
    from app.services.mock_ai_service import MockAIService
    
    mock_service = MockAIService()
    
    # Replace the global AI service instance
    original_service = ai_service_instance._service
    ai_service_instance._service = mock_service
    
    yield mock_service
    
    # Restore original service
    ai_service_instance._service = original_service


@pytest.fixture
def sample_text_request():
    """Sample text modification request for testing."""
    from app.models.requests import TextModificationRequest, TextOperation
    
    return TextModificationRequest(
        text="This is a test text that needs improvement.",
        operation=TextOperation.IMPROVE,
        user_id="test_user",
        preserve_formatting=True
    )


@pytest.fixture
def sample_background_request():
    """Sample background text request for testing."""
    from app.models.requests import BackgroundTextRequest, TextOperation
    
    return BackgroundTextRequest(
        text="This is a test text for background processing.",
        operation=TextOperation.SUMMARIZE,
        source_application="notepad.exe",
        user_id="test_user"
    )