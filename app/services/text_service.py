"""
Text processing service that coordinates AI operations and data persistence.
"""

from datetime import datetime
from typing import Dict, Any, List, Optional
import structlog

from app.config.database import get_collection
from app.models.requests import TextModificationRequest, TextOperation
from app.models.responses import TextModificationResponse, ModificationHistoryResponse
from app.models.database import ModificationRecord
from app.models.validation import sanitize_text_input
from app.services.ai_service import get_ai_service
from app.middlewares.error_handler import TextProcessingError

logger = structlog.get_logger(__name__)


class TextService:
    """Service for text processing operations with AI integration and persistence."""
    
    def __init__(self):
        self.collection_name = "modification_records"
    
    async def process_text_modification(self, request: TextModificationRequest) -> TextModificationResponse:
        """
        Process text modification request with AI and store results.
        
        Args:
            request: Text modification request
            
        Returns:
            TextModificationResponse: Processing results
            
        Raises:
            TextProcessingError: If processing fails
        """
        try:
            # Sanitize input text
            sanitized_text = sanitize_text_input(request.text)
            if not sanitized_text:
                raise TextProcessingError("Text is empty after sanitization", request.operation.value)
            
            # Get AI service
            ai_service = await get_ai_service()
            
            # Prepare AI service parameters
            ai_params = {}
            if request.target_language:
                ai_params['target_language'] = request.target_language
            if request.options:
                ai_params.update(request.options)
            
            # Process with AI service
            logger.info(
                "Processing text modification",
                operation=request.operation.value,
                text_length=len(sanitized_text),
                user_id=request.user_id
            )
            
            ai_result = await ai_service.modify_text(
                sanitized_text,
                request.operation,
                **ai_params
            )
            
            # Calculate word counts
            word_count_original = len(sanitized_text.split())
            word_count_modified = len(ai_result["modified_text"].split())
            
            # Create response
            response = TextModificationResponse(
                original_text=sanitized_text,
                modified_text=ai_result["modified_text"],
                operation=request.operation,
                timestamp=datetime.utcnow(),
                processing_time=ai_result["processing_time"],
                user_id=request.user_id,
                ai_model_used=ai_result["ai_model_used"],
                confidence_score=ai_result.get("confidence_score"),
                word_count_original=word_count_original,
                word_count_modified=word_count_modified,
                metadata=ai_result.get("metadata", {})
            )
            
            # Store in database
            await self._store_modification_record(request, response, ai_result)
            
            logger.info(
                "Text modification completed successfully",
                operation=request.operation.value,
                processing_time=ai_result["processing_time"],
                user_id=request.user_id,
                word_count_change=word_count_modified - word_count_original
            )
            
            return response
            
        except Exception as e:
            logger.error(
                "Text modification failed",
                operation=request.operation.value if hasattr(request, 'operation') else 'unknown',
                error=str(e),
                error_type=type(e).__name__,
                user_id=getattr(request, 'user_id', None)
            )
            
            if isinstance(e, TextProcessingError):
                raise
            else:
                raise TextProcessingError(
                    f"Text processing failed: {str(e)}",
                    request.operation.value if hasattr(request, 'operation') else None,
                    is_retryable=True
                )
    
    async def get_modification_history(
        self, 
        user_id: str, 
        page: int = 1, 
        page_size: int = 10,
        operation_filter: Optional[TextOperation] = None
    ) -> ModificationHistoryResponse:
        """
        Get modification history for a user.
        
        Args:
            user_id: User identifier
            page: Page number (1-based)
            page_size: Number of items per page
            operation_filter: Optional operation type filter
            
        Returns:
            ModificationHistoryResponse: User's modification history
        """
        try:
            collection = await get_collection(self.collection_name)
            
            # Build query
            query = {"user_id": user_id}
            if operation_filter:
                query["operation"] = operation_filter.value
            
            # Calculate skip value
            skip = (page - 1) * page_size
            
            # Get total count
            total_count = await collection.count_documents(query)
            
            # Get modifications with pagination
            cursor = collection.find(query).sort("timestamp", -1).skip(skip).limit(page_size)
            modifications = await cursor.to_list(length=page_size)
            
            # Convert to response format
            modification_list = []
            for mod in modifications:
                modification_list.append({
                    "id": str(mod["_id"]),
                    "original_text": mod["original_text"][:100] + "..." if len(mod["original_text"]) > 100 else mod["original_text"],
                    "modified_text": mod["modified_text"][:100] + "..." if len(mod["modified_text"]) > 100 else mod["modified_text"],
                    "operation": mod["operation"],
                    "timestamp": mod["timestamp"],
                    "processing_time": mod["processing_time"],
                    "ai_model_used": mod["ai_model_used"],
                    "confidence_score": mod.get("confidence_score"),
                    "word_count_original": mod["word_count_original"],
                    "word_count_modified": mod["word_count_modified"]
                })
            
            # Calculate total pages
            total_pages = (total_count + page_size - 1) // page_size
            
            return ModificationHistoryResponse(
                user_id=user_id,
                total_modifications=total_count,
                modifications=modification_list,
                page=page,
                page_size=page_size,
                total_pages=total_pages
            )
            
        except Exception as e:
            logger.error(
                "Failed to get modification history",
                user_id=user_id,
                error=str(e),
                error_type=type(e).__name__
            )
            raise TextProcessingError(
                f"Failed to retrieve modification history: {str(e)}",
                is_retryable=True
            )
    
    async def analyze_text(self, text: str, user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyze text using AI service.
        
        Args:
            text: Text to analyze
            user_id: Optional user identifier
            
        Returns:
            Dict containing analysis results
        """
        try:
            # Sanitize input
            sanitized_text = sanitize_text_input(text)
            if not sanitized_text:
                raise TextProcessingError("Text is empty after sanitization")
            
            # Get AI service
            ai_service = await get_ai_service()
            
            # Perform analysis
            logger.info(
                "Analyzing text",
                text_length=len(sanitized_text),
                user_id=user_id
            )
            
            analysis_result = await ai_service.analyze_text(sanitized_text)
            
            logger.info(
                "Text analysis completed",
                user_id=user_id,
                word_count=analysis_result.get("word_count", 0)
            )
            
            return analysis_result
            
        except Exception as e:
            logger.error(
                "Text analysis failed",
                error=str(e),
                error_type=type(e).__name__,
                user_id=user_id
            )
            raise TextProcessingError(
                f"Text analysis failed: {str(e)}",
                is_retryable=True
            )
    
    async def get_user_statistics(self, user_id: str) -> Dict[str, Any]:
        """
        Get statistics for a user's text modifications.
        
        Args:
            user_id: User identifier
            
        Returns:
            Dict containing user statistics
        """
        try:
            collection = await get_collection(self.collection_name)
            
            # Aggregation pipeline for statistics
            pipeline = [
                {"$match": {"user_id": user_id}},
                {
                    "$group": {
                        "_id": None,
                        "total_modifications": {"$sum": 1},
                        "total_processing_time": {"$sum": "$processing_time"},
                        "avg_processing_time": {"$avg": "$processing_time"},
                        "total_words_processed": {"$sum": "$word_count_original"},
                        "operations_count": {
                            "$push": "$operation"
                        },
                        "first_modification": {"$min": "$timestamp"},
                        "last_modification": {"$max": "$timestamp"}
                    }
                }
            ]
            
            result = await collection.aggregate(pipeline).to_list(length=1)
            
            if not result:
                return {
                    "user_id": user_id,
                    "total_modifications": 0,
                    "total_processing_time": 0.0,
                    "avg_processing_time": 0.0,
                    "total_words_processed": 0,
                    "operations_breakdown": {},
                    "first_modification": None,
                    "last_modification": None
                }
            
            stats = result[0]
            
            # Count operations
            operations_breakdown = {}
            for op in stats["operations_count"]:
                operations_breakdown[op] = operations_breakdown.get(op, 0) + 1
            
            return {
                "user_id": user_id,
                "total_modifications": stats["total_modifications"],
                "total_processing_time": round(stats["total_processing_time"], 2),
                "avg_processing_time": round(stats["avg_processing_time"], 2),
                "total_words_processed": stats["total_words_processed"],
                "operations_breakdown": operations_breakdown,
                "first_modification": stats["first_modification"],
                "last_modification": stats["last_modification"]
            }
            
        except Exception as e:
            logger.error(
                "Failed to get user statistics",
                user_id=user_id,
                error=str(e),
                error_type=type(e).__name__
            )
            raise TextProcessingError(
                f"Failed to retrieve user statistics: {str(e)}",
                is_retryable=True
            )
    
    async def _store_modification_record(
        self, 
        request: TextModificationRequest, 
        response: TextModificationResponse,
        ai_result: Dict[str, Any]
    ):
        """Store modification record in database."""
        try:
            collection = await get_collection(self.collection_name)
            
            record = ModificationRecord(
                user_id=request.user_id,
                original_text=response.original_text,
                modified_text=response.modified_text,
                operation=request.operation,
                timestamp=response.timestamp,
                processing_time=response.processing_time,
                ai_model_used=response.ai_model_used,
                confidence_score=response.confidence_score,
                word_count_original=response.word_count_original,
                word_count_modified=response.word_count_modified,
                target_language=request.target_language,
                preserve_formatting=request.preserve_formatting,
                options=request.options,
                metadata=response.metadata
            )
            
            # Insert record
            result = await collection.insert_one(record.dict(by_alias=True, exclude_unset=True))
            
            logger.debug(
                "Modification record stored",
                record_id=str(result.inserted_id),
                user_id=request.user_id,
                operation=request.operation.value
            )
            
        except Exception as e:
            # Log error but don't fail the main operation
            logger.error(
                "Failed to store modification record",
                error=str(e),
                error_type=type(e).__name__,
                user_id=request.user_id,
                operation=request.operation.value
            )


# Global text service instance
text_service = TextService()


async def get_text_service() -> TextService:
    """Dependency function to get text service instance."""
    return text_service