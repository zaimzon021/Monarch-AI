"""
Tests for controller layer components.
"""

import pytest
from unittest.mock import AsyncMock, patch
from fastapi import Request
from fastapi.testclient import TestClient

from app.controllers.text_controller import TextController
from app.models.requests import TextModificationRequest, TextOperation


class TestTextController:
    """Test cases for TextController."""
    
    @pytest.fixture
    def controller(self):
        return TextController()
    
    @pytest.fixture
    def mock_request(self):
        """Mock FastAPI request object."""
        request = AsyncMock(spec=Request)
        request.state.correlation_id = "test-correlation-id"
        request.method = "POST"
        request.url.path = "/api/v1/text/modify"
        return request
    
    @pytest.mark.asyncio
    async def test_process_text_modification_success(self, controller, mock_request, sample_text_request):
        """Test successful text modification processing."""
        with patch('app.controllers.text_controller.get_text_service') as mock_get_service:
            mock_service = AsyncMock()
            mock_get_service.return_value = mock_service
            
            # Mock service response
            from app.models.responses import TextModificationResponse
            from datetime import datetime
            
            mock_response = TextModificationResponse(
                original_text=sample_text_request.text,
                modified_text="This is an improved test text with better clarity and structure.",
                operation=sample_text_request.operation,
                timestamp=datetime.utcnow(),
                processing_time=1.5,
                user_id=sample_text_request.user_id,
                ai_model_used="gpt-3.5-turbo",
                word_count_original=9,
                word_count_modified=11
            )
            mock_service.process_text_modification.return_value = mock_response
            
            # Mock validation
            with patch('app.controllers.text_controller.validate_text_modification_request') as mock_validate:
                mock_validate.return_value = (True, [])
                
                result = await controller.process_text_modification(
                    mock_request, 
                    sample_text_request, 
                    mock_service
                )
                
                assert result.original_text == sample_text_request.text
                assert result.operation == sample_text_request.operation
                assert result.processing_time > 0
    
    @pytest.mark.asyncio
    async def test_process_text_modification_validation_error(self, controller, mock_request, sample_text_request):
        """Test text modification with validation error."""
        with patch('app.controllers.text_controller.get_text_service') as mock_get_service:
            mock_service = AsyncMock()
            mock_get_service.return_value = mock_service
            
            # Mock validation failure
            with patch('app.controllers.text_controller.validate_text_modification_request') as mock_validate:
                mock_validate.return_value = (False, ["Text is too long"])
                
                from fastapi import HTTPException
                
                with pytest.raises(HTTPException) as exc_info:
                    await controller.process_text_modification(
                        mock_request, 
                        sample_text_request, 
                        mock_service
                    )
                
                assert exc_info.value.status_code == 422
    
    @pytest.mark.asyncio
    async def test_get_modification_history_success(self, controller, mock_request):
        """Test successful modification history retrieval."""
        with patch('app.controllers.text_controller.get_text_service') as mock_get_service:
            mock_service = AsyncMock()
            mock_get_service.return_value = mock_service
            
            # Mock service response
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
            
            result = await controller.get_modification_history(
                mock_request,
                "test_user",
                1,
                10,
                None,
                mock_service
            )
            
            assert result.user_id == "test_user"
            assert result.total_modifications == 5
    
    @pytest.mark.asyncio
    async def test_get_modification_history_invalid_page(self, controller, mock_request):
        """Test modification history with invalid page number."""
        with patch('app.controllers.text_controller.get_text_service') as mock_get_service:
            mock_service = AsyncMock()
            mock_get_service.return_value = mock_service
            
            from fastapi import HTTPException
            
            with pytest.raises(HTTPException) as exc_info:
                await controller.get_modification_history(
                    mock_request,
                    "test_user",
                    0,  # Invalid page number
                    10,
                    None,
                    mock_service
                )
            
            assert exc_info.value.status_code == 400
    
    @pytest.mark.asyncio
    async def test_analyze_text_success(self, controller, mock_request):
        """Test successful text analysis."""
        with patch('app.controllers.text_controller.get_text_service') as mock_get_service:
            mock_service = AsyncMock()
            mock_get_service.return_value = mock_service
            
            # Mock service response
            mock_analysis = {
                "word_count": 5,
                "sentiment": "neutral",
                "topics": ["test", "analysis"],
                "reading_level": "intermediate"
            }
            mock_service.analyze_text.return_value = mock_analysis
            
            result = await controller.analyze_text(
                mock_request,
                "This is test text",
                "test_user",
                mock_service
            )
            
            assert result["word_count"] == 5
            assert result["sentiment"] == "neutral"
    
    @pytest.mark.asyncio
    async def test_analyze_text_empty_text(self, controller, mock_request):
        """Test text analysis with empty text."""
        with patch('app.controllers.text_controller.get_text_service') as mock_get_service:
            mock_service = AsyncMock()
            mock_get_service.return_value = mock_service
            
            from fastapi import HTTPException
            
            with pytest.raises(HTTPException) as exc_info:
                await controller.analyze_text(
                    mock_request,
                    "",  # Empty text
                    "test_user",
                    mock_service
                )
            
            assert exc_info.value.status_code == 400
    
    @pytest.mark.asyncio
    async def test_get_supported_operations(self, controller, mock_request):
        """Test getting supported operations."""
        result = await controller.get_supported_operations(mock_request)
        
        assert "operations" in result
        assert len(result["operations"]) > 0
        
        # Check that all text operations are included
        operation_names = [op["name"] for op in result["operations"]]
        expected_operations = [op.value for op in TextOperation]
        
        for expected_op in expected_operations:
            assert expected_op in operation_names