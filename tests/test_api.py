"""
Tests for API endpoints and integration.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock

from app.main import app


class TestAPIEndpoints:
    """Test cases for API endpoints."""
    
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    def test_root_endpoint(self, client):
        """Test root endpoint."""
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert "service" in data
        assert "version" in data
        assert "status" in data
    
    def test_ping_endpoint(self, client):
        """Test ping endpoint."""
        response = client.get("/ping")
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "pong"
    
    def test_api_root_endpoint(self, client):
        """Test API root endpoint."""
        response = client.get("/api/v1/")
        
        assert response.status_code == 200
        data = response.json()
        assert "service" in data
        assert "endpoints" in data
        assert "text_modification" in data["endpoints"]
    
    @patch('app.config.database_init.check_database_health')
    @patch('app.services.ai_service.get_ai_service')
    def test_health_check_endpoint(self, mock_get_ai_service, mock_db_health, client):
        """Test health check endpoint."""
        # Mock database health
        mock_db_health.return_value = {"status": "healthy"}
        
        # Mock AI service health
        mock_ai_service = AsyncMock()
        mock_ai_service.health_check.return_value = {"status": "healthy"}
        mock_get_ai_service.return_value = mock_ai_service
        
        response = client.get("/api/v1/health")
        
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "timestamp" in data
        assert "version" in data
    
    def test_status_endpoint(self, client):
        """Test status endpoint."""
        response = client.get("/api/v1/status")
        
        assert response.status_code == 200
        data = response.json()
        assert "service_name" in data
        assert "version" in data
        assert "status" in data
        assert "features" in data
    
    def test_supported_operations_endpoint(self, client):
        """Test supported operations endpoint."""
        response = client.get("/api/v1/text/operations")
        
        assert response.status_code == 200
        data = response.json()
        assert "operations" in data
        assert len(data["operations"]) > 0
        
        # Check operation structure
        operation = data["operations"][0]
        assert "name" in operation
        assert "description" in operation
    
    @patch('app.services.text_service.get_text_service')
    def test_text_modification_endpoint(self, mock_get_service, client):
        """Test text modification endpoint."""
        # Mock text service
        mock_service = AsyncMock()
        mock_get_service.return_value = mock_service
        
        from app.models.responses import TextModificationResponse
        from datetime import datetime
        
        mock_response = TextModificationResponse(
            original_text="Test text",
            modified_text="Improved test text",
            operation="improve",
            timestamp=datetime.utcnow(),
            processing_time=1.5,
            user_id="test_user",
            ai_model_used="gpt-3.5-turbo",
            word_count_original=2,
            word_count_modified=3
        )
        mock_service.process_text_modification.return_value = mock_response
        
        # Mock validation
        with patch('app.models.validation.validate_text_modification_request') as mock_validate:
            mock_validate.return_value = (True, [])
            
            request_data = {
                "text": "Test text",
                "operation": "improve",
                "user_id": "test_user"
            }
            
            response = client.post("/api/v1/text/modify", json=request_data)
            
            assert response.status_code == 200
            data = response.json()
            assert data["original_text"] == "Test text"
            assert data["operation"] == "improve"
    
    def test_text_modification_validation_error(self, client):
        """Test text modification with validation error."""
        request_data = {
            "text": "",  # Empty text should cause validation error
            "operation": "improve"
        }
        
        response = client.post("/api/v1/text/modify", json=request_data)
        
        assert response.status_code == 422  # Validation error
    
    def test_text_modification_invalid_operation(self, client):
        """Test text modification with invalid operation."""
        request_data = {
            "text": "Test text",
            "operation": "invalid_operation"
        }
        
        response = client.post("/api/v1/text/modify", json=request_data)
        
        assert response.status_code == 422  # Validation error
    
    @patch('app.services.text_service.get_text_service')
    def test_text_analysis_endpoint(self, mock_get_service, client):
        """Test text analysis endpoint."""
        # Mock text service
        mock_service = AsyncMock()
        mock_get_service.return_value = mock_service
        
        mock_analysis = {
            "word_count": 5,
            "sentiment": "neutral",
            "topics": ["test", "analysis"],
            "reading_level": "intermediate"
        }
        mock_service.analyze_text.return_value = mock_analysis
        
        request_data = {
            "text": "This is test text for analysis",
            "user_id": "test_user"
        }
        
        response = client.post("/api/v1/text/analyze", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["word_count"] == 5
        assert data["sentiment"] == "neutral"
    
    @patch('app.services.text_service.get_text_service')
    def test_modification_history_endpoint(self, mock_get_service, client):
        """Test modification history endpoint."""
        # Mock text service
        mock_service = AsyncMock()
        mock_get_service.return_value = mock_service
        
        from app.models.responses import ModificationHistoryResponse
        
        mock_response = ModificationHistoryResponse(
            user_id="test_user",
            total_modifications=5,
            modifications=[],
            page=1,
            page_size=10,
            total_pages=1
        )
        mock_service.get_modification_history.return_value = mock_response
        
        response = client.get("/api/v1/text/history/test_user")
        
        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == "test_user"
        assert data["total_modifications"] == 5
    
    def test_modification_history_pagination(self, client):
        """Test modification history with pagination parameters."""
        with patch('app.services.text_service.get_text_service') as mock_get_service:
            mock_service = AsyncMock()
            mock_get_service.return_value = mock_service
            
            from app.models.responses import ModificationHistoryResponse
            
            mock_response = ModificationHistoryResponse(
                user_id="test_user",
                total_modifications=25,
                modifications=[],
                page=2,
                page_size=5,
                total_pages=5
            )
            mock_service.get_modification_history.return_value = mock_response
            
            response = client.get("/api/v1/text/history/test_user?page=2&page_size=5")
            
            assert response.status_code == 200
            data = response.json()
            assert data["page"] == 2
            assert data["page_size"] == 5
    
    @patch('app.services.text_service.get_text_service')
    def test_user_statistics_endpoint(self, mock_get_service, client):
        """Test user statistics endpoint."""
        # Mock text service
        mock_service = AsyncMock()
        mock_get_service.return_value = mock_service
        
        mock_stats = {
            "user_id": "test_user",
            "total_modifications": 10,
            "total_processing_time": 15.5,
            "avg_processing_time": 1.55,
            "operations_breakdown": {
                "improve": 5,
                "summarize": 3,
                "translate": 2
            }
        }
        mock_service.get_user_statistics.return_value = mock_stats
        
        response = client.get("/api/v1/text/statistics/test_user")
        
        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == "test_user"
        assert data["total_modifications"] == 10
        assert "operations_breakdown" in data
    
    def test_cors_headers(self, client):
        """Test CORS headers are present."""
        response = client.options("/api/v1/text/operations")
        
        # CORS headers should be present
        assert "access-control-allow-origin" in response.headers
        assert "access-control-allow-methods" in response.headers
    
    def test_correlation_id_header(self, client):
        """Test correlation ID header is added to responses."""
        response = client.get("/api/v1/text/operations")
        
        assert response.status_code == 200
        assert "x-correlation-id" in response.headers
        assert "x-process-time" in response.headers


class TestErrorHandling:
    """Test cases for error handling."""
    
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    def test_404_error(self, client):
        """Test 404 error handling."""
        response = client.get("/nonexistent-endpoint")
        
        assert response.status_code == 404
    
    def test_method_not_allowed(self, client):
        """Test 405 method not allowed error."""
        response = client.put("/api/v1/text/operations")  # PUT not allowed
        
        assert response.status_code == 405
    
    @patch('app.services.text_service.get_text_service')
    def test_internal_server_error(self, mock_get_service, client):
        """Test 500 internal server error handling."""
        # Mock service to raise exception
        mock_service = AsyncMock()
        mock_get_service.return_value = mock_service
        mock_service.get_user_statistics.side_effect = Exception("Test error")
        
        response = client.get("/api/v1/text/statistics/test_user")
        
        assert response.status_code == 500
        data = response.json()
        assert "error" in data
        assert "correlation_id" in data or "request_id" in data