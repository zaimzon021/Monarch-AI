"""
Integration tests for the complete application.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock

from app.main import app


class TestApplicationIntegration:
    """Test complete application integration."""
    
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    def test_application_startup(self, client):
        """Test that the application starts up correctly."""
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert "service" in data
        assert "version" in data
        assert data["status"] == "operational"
    
    def test_api_documentation_available(self, client):
        """Test that API documentation is accessible."""
        response = client.get("/docs")
        assert response.status_code == 200
        
        response = client.get("/openapi.json")
        assert response.status_code == 200
        
        openapi_spec = response.json()
        assert "openapi" in openapi_spec
        assert "info" in openapi_spec
        assert "paths" in openapi_spec
    
    @patch('app.config.database_init.check_database_health')
    @patch('app.services.ai_service.get_ai_service')
    def test_health_check_integration(self, mock_get_ai_service, mock_db_health, client):
        """Test complete health check integration."""
        # Mock database health
        mock_db_health.return_value = {
            "status": "healthy",
            "connected": True,
            "database": "ai_text_assistant"
        }
        
        # Mock AI service health
        mock_ai_service = AsyncMock()
        mock_ai_service.health_check.return_value = {
            "status": "healthy",
            "response_time": 0.1
        }
        mock_get_ai_service.return_value = mock_ai_service
        
        response = client.get("/api/v1/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] in ["healthy", "degraded"]
        assert "timestamp" in data
        assert "version" in data
        assert "database" in data
        assert "ai_service" in data
    
    def test_cors_headers_present(self, client):
        """Test that CORS headers are properly configured."""
        response = client.options("/api/v1/text/operations")
        
        assert "access-control-allow-origin" in response.headers
        assert "access-control-allow-methods" in response.headers
        assert "access-control-allow-headers" in response.headers
    
    def test_request_correlation_id(self, client):
        """Test that correlation IDs are added to all responses."""
        response = client.get("/api/v1/text/operations")
        
        assert response.status_code == 200
        assert "x-correlation-id" in response.headers
        assert "x-process-time" in response.headers
    
    @patch('app.services.text_service.get_text_service')
    def test_complete_text_modification_flow(self, mock_get_service, client):
        """Test complete text modification flow from API to service."""
        # Mock text service
        mock_service = AsyncMock()
        mock_get_service.return_value = mock_service
        
        from app.models.responses import TextModificationResponse
        from datetime import datetime
        
        mock_response = TextModificationResponse(
            original_text="Test text",
            modified_text="Improved test text with better clarity and structure.",
            operation="improve",
            timestamp=datetime.utcnow(),
            processing_time=1.5,
            user_id="test_user",
            ai_model_used="gpt-3.5-turbo",
            word_count_original=2,
            word_count_modified=8
        )
        mock_service.process_text_modification.return_value = mock_response
        
        # Mock validation
        with patch('app.models.validation.validate_text_modification_request') as mock_validate:
            mock_validate.return_value = (True, [])
            
            request_data = {
                "text": "Test text",
                "operation": "improve",
                "user_id": "test_user",
                "preserve_formatting": True
            }
            
            response = client.post("/api/v1/text/modify", json=request_data)
            
            assert response.status_code == 200
            data = response.json()
            
            # Verify response structure
            assert data["original_text"] == "Test text"
            assert data["modified_text"] == "Improved test text with better clarity and structure."
            assert data["operation"] == "improve"
            assert data["user_id"] == "test_user"
            assert data["processing_time"] == 1.5
            assert data["word_count_original"] == 2
            assert data["word_count_modified"] == 8
            
            # Verify service was called
            mock_service.process_text_modification.assert_called_once()
    
    def test_error_handling_integration(self, client):
        """Test that error handling works across the application."""
        # Test validation error
        response = client.post("/api/v1/text/modify", json={
            "text": "",  # Empty text should cause validation error
            "operation": "improve"
        })
        
        assert response.status_code == 422
        data = response.json()
        assert "error" in data or "detail" in data
        
        # Test 404 error
        response = client.get("/nonexistent-endpoint")
        assert response.status_code == 404
    
    def test_middleware_integration(self, client):
        """Test that all middleware is properly integrated."""
        response = client.get("/api/v1/text/operations")
        
        assert response.status_code == 200
        
        # Check logging middleware headers
        assert "x-correlation-id" in response.headers
        
        # Check timing middleware headers
        assert "x-process-time" in response.headers
        
        # Check CORS middleware headers
        assert "access-control-allow-origin" in response.headers
    
    @patch('app.services.text_service.get_text_service')
    def test_user_statistics_integration(self, mock_get_service, client):
        """Test user statistics endpoint integration."""
        mock_service = AsyncMock()
        mock_get_service.return_value = mock_service
        
        mock_stats = {
            "user_id": "test_user",
            "total_modifications": 15,
            "total_processing_time": 23.5,
            "avg_processing_time": 1.57,
            "total_words_processed": 450,
            "operations_breakdown": {
                "improve": 8,
                "summarize": 4,
                "translate": 3
            },
            "first_modification": "2023-01-01T10:00:00Z",
            "last_modification": "2023-12-01T15:30:00Z"
        }
        mock_service.get_user_statistics.return_value = mock_stats
        
        response = client.get("/api/v1/text/statistics/test_user")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["user_id"] == "test_user"
        assert data["total_modifications"] == 15
        assert data["operations_breakdown"]["improve"] == 8
    
    def test_api_versioning(self, client):
        """Test that API versioning is properly implemented."""
        # Test v1 API root
        response = client.get("/api/v1/")
        assert response.status_code == 200
        
        data = response.json()
        assert "endpoints" in data
        assert "text_modification" in data["endpoints"]
        assert "/api/v1/text/modify" in data["endpoints"]["text_modification"]
    
    def test_openapi_spec_completeness(self, client):
        """Test that OpenAPI specification is complete."""
        response = client.get("/openapi.json")
        assert response.status_code == 200
        
        spec = response.json()
        
        # Check basic structure
        assert "openapi" in spec
        assert "info" in spec
        assert "paths" in spec
        assert "components" in spec
        
        # Check that main endpoints are documented
        paths = spec["paths"]
        assert "/api/v1/text/modify" in paths
        assert "/api/v1/text/history/{user_id}" in paths
        assert "/api/v1/text/analyze" in paths
        assert "/api/v1/health" in paths
        
        # Check that models are defined
        components = spec["components"]
        assert "schemas" in components
        schemas = components["schemas"]
        assert "TextModificationRequest" in schemas
        assert "TextModificationResponse" in schemas
        assert "ErrorResponse" in schemas