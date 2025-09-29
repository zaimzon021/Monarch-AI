"""
Tests for service layer components.
"""

import pytest
from unittest.mock import AsyncMock, patch
from datetime import datetime

from app.services.text_service import TextService
from app.services.ai_service import AIService
from app.models.requests import TextModificationRequest, TextOperation
from app.middlewares.error_handler import TextProcessingError


class TestTextService:
    """Test cases for TextService."""
    
    @pytest.fixture
    def text_service(self):
        return TextService()
    
    @pytest.mark.asyncio
    async def test_process_text_modification_success(self, text_service, sample_text_request, mock_ai_service):
        """Test successful text modification processing."""
        # Mock database collection
        with patch('app.services.text_service.get_collection') as mock_get_collection:
            mock_collection = AsyncMock()
            mock_get_collection.return_value = mock_collection
            mock_collection.insert_one.return_value = AsyncMock(inserted_id="test_id")
            
            result = await text_service.process_text_modification(sample_text_request)
            
            assert result.original_text == sample_text_request.text
            assert result.operation == sample_text_request.operation
            assert result.user_id == sample_text_request.user_id
            assert result.processing_time > 0
            assert result.word_count_original > 0
            assert result.word_count_modified > 0
    
    @pytest.mark.asyncio
    async def test_process_text_modification_empty_text(self, text_service):
        """Test text modification with empty text."""
        from app.models.requests import TextModificationRequest, TextOperation
        
        request = TextModificationRequest(
            text="   ",  # Empty after sanitization
            operation=TextOperation.IMPROVE,
            user_id="test_user"
        )
        
        with pytest.raises(TextProcessingError) as exc_info:
            await text_service.process_text_modification(request)
        
        assert "empty after sanitization" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_get_modification_history(self, text_service):
        """Test getting modification history."""
        with patch('app.services.text_service.get_collection') as mock_get_collection:
            mock_collection = AsyncMock()
            mock_get_collection.return_value = mock_collection
            
            # Mock database responses
            mock_collection.count_documents.return_value = 5
            mock_cursor = AsyncMock()
            mock_cursor.to_list.return_value = [
                {
                    "_id": "test_id",
                    "original_text": "Test text",
                    "modified_text": "Improved test text",
                    "operation": "improve",
                    "timestamp": datetime.utcnow(),
                    "processing_time": 1.5,
                    "ai_model_used": "gpt-3.5-turbo",
                    "word_count_original": 2,
                    "word_count_modified": 3
                }
            ]
            mock_collection.find.return_value = mock_cursor
            mock_cursor.sort.return_value = mock_cursor
            mock_cursor.skip.return_value = mock_cursor
            mock_cursor.limit.return_value = mock_cursor
            
            result = await text_service.get_modification_history("test_user")
            
            assert result.user_id == "test_user"
            assert result.total_modifications == 5
            assert len(result.modifications) == 1
            assert result.page == 1
            assert result.page_size == 10
    
    @pytest.mark.asyncio
    async def test_analyze_text(self, text_service, mock_ai_service):
        """Test text analysis."""
        result = await text_service.analyze_text("This is test text", "test_user")
        
        assert "word_count" in result
        assert "sentiment" in result
        assert result["word_count"] > 0


class TestAIService:
    """Test cases for AIService."""
    
    @pytest.fixture
    def ai_service(self):
        return AIService()
    
    @pytest.mark.asyncio
    async def test_modify_text_success(self, ai_service):
        """Test successful text modification."""
        with patch('httpx.AsyncClient.post') as mock_post:
            mock_response = AsyncMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "choices": [{
                    "message": {
                        "content": "This is an improved test text with better clarity and structure."
                    }
                }],
                "usage": {"total_tokens": 25}
            }
            mock_post.return_value = mock_response
            
            result = await ai_service.modify_text(
                "This is a test text that needs improvement.",
                TextOperation.IMPROVE
            )
            
            assert "modified_text" in result
            assert "processing_time" in result
            assert "ai_model_used" in result
            assert result["processing_time"] > 0
    
    @pytest.mark.asyncio
    async def test_modify_text_api_error(self, ai_service):
        """Test AI service API error handling."""
        with patch('httpx.AsyncClient.post') as mock_post:
            mock_response = AsyncMock()
            mock_response.status_code = 500
            mock_response.text = "Internal Server Error"
            mock_post.return_value = mock_response
            
            from app.middlewares.error_handler import AIServiceError
            
            with pytest.raises(AIServiceError):
                await ai_service.modify_text(
                    "Test text",
                    TextOperation.IMPROVE
                )
    
    @pytest.mark.asyncio
    async def test_health_check(self, ai_service):
        """Test AI service health check."""
        with patch('httpx.AsyncClient.get') as mock_get:
            mock_response = AsyncMock()
            mock_response.status_code = 200
            mock_get.return_value = mock_response
            
            result = await ai_service.health_check()
            
            assert "status" in result
            assert result["status"] == "healthy"