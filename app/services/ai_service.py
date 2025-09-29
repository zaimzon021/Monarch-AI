"""
AI service integration for text modification operations.
"""

import asyncio
import json
from typing import Dict, Any, Optional
from datetime import datetime
import httpx
import structlog

from app.config.settings import settings
from app.models.requests import TextOperation
from app.middlewares.error_handler import AIServiceError

logger = structlog.get_logger(__name__)


class AIService:
    """Service for integrating with AI APIs for text modification."""
    
    def __init__(self):
        self.client: Optional[httpx.AsyncClient] = None
        self.base_url = settings.ai_api_endpoint
        self.api_key = settings.ai_api_key
        self.model = settings.ai_model
        self.timeout = settings.ai_api_timeout
        
    async def __aenter__(self):
        """Async context manager entry."""
        await self.initialize()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
    
    async def initialize(self):
        """Initialize the HTTP client for AI service communication."""
        if self.client is None:
            self.client = httpx.AsyncClient(
                timeout=httpx.Timeout(self.timeout),
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                    "User-Agent": "AI-Text-Assistant/1.0.0"
                }
            )
            logger.info("AI service client initialized")
    
    async def close(self):
        """Close the HTTP client."""
        if self.client:
            await self.client.aclose()
            self.client = None
            logger.info("AI service client closed")
    
    async def modify_text(self, text: str, operation: TextOperation, **kwargs) -> Dict[str, Any]:
        """
        Modify text using AI service.
        
        Args:
            text: Text to modify
            operation: Type of modification to perform
            **kwargs: Additional options for the operation
            
        Returns:
            Dict containing modified text and metadata
            
        Raises:
            AIServiceError: If AI service operation fails
        """
        if not self.client:
            await self.initialize()
        
        try:
            # Build the prompt based on operation
            prompt = self._build_prompt(text, operation, **kwargs)
            
            # Prepare request payload
            payload = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": self._get_system_prompt(operation)},
                    {"role": "user", "content": prompt}
                ],
                "temperature": kwargs.get("temperature", 0.7),
                "max_tokens": kwargs.get("max_tokens", 2000),
                "top_p": kwargs.get("top_p", 1.0)
            }
            
            # Log the request (without sensitive data)
            logger.info(
                "Making AI service request",
                operation=operation.value,
                text_length=len(text),
                model=self.model
            )
            
            # Make the API request
            start_time = datetime.utcnow()
            response = await self.client.post(
                f"{self.base_url}/chat/completions",
                json=payload
            )
            end_time = datetime.utcnow()
            processing_time = (end_time - start_time).total_seconds()
            
            # Handle response
            if response.status_code == 200:
                result = response.json()
                modified_text = result["choices"][0]["message"]["content"].strip()
                
                # Extract metadata
                usage = result.get("usage", {})
                
                logger.info(
                    "AI service request successful",
                    operation=operation.value,
                    processing_time=processing_time,
                    tokens_used=usage.get("total_tokens", 0)
                )
                
                return {
                    "modified_text": modified_text,
                    "original_text": text,
                    "operation": operation.value,
                    "processing_time": processing_time,
                    "ai_model_used": self.model,
                    "tokens_used": usage.get("total_tokens", 0),
                    "prompt_tokens": usage.get("prompt_tokens", 0),
                    "completion_tokens": usage.get("completion_tokens", 0),
                    "confidence_score": self._calculate_confidence_score(result),
                    "metadata": {
                        "finish_reason": result["choices"][0].get("finish_reason"),
                        "model": result.get("model", self.model)
                    }
                }
            else:
                error_detail = response.text
                logger.error(
                    "AI service request failed",
                    status_code=response.status_code,
                    error=error_detail,
                    operation=operation.value
                )
                raise AIServiceError(
                    f"AI service returned status {response.status_code}: {error_detail}",
                    status_code=response.status_code,
                    is_retryable=response.status_code >= 500
                )
                
        except httpx.TimeoutException:
            logger.error("AI service request timed out", operation=operation.value)
            raise AIServiceError(
                "AI service request timed out",
                status_code=504,
                is_retryable=True
            )
        except httpx.RequestError as e:
            logger.error("AI service request error", error=str(e), operation=operation.value)
            raise AIServiceError(
                f"AI service request failed: {str(e)}",
                status_code=502,
                is_retryable=True
            )
        except Exception as e:
            logger.error("Unexpected AI service error", error=str(e), operation=operation.value)
            raise AIServiceError(
                f"Unexpected AI service error: {str(e)}",
                status_code=500,
                is_retryable=False
            )
    
    async def analyze_text(self, text: str) -> Dict[str, Any]:
        """
        Analyze text for various metrics and insights.
        
        Args:
            text: Text to analyze
            
        Returns:
            Dict containing analysis results
        """
        if not self.client:
            await self.initialize()
        
        try:
            prompt = f"""Analyze the following text and provide insights:

Text: "{text}"

Please provide analysis in the following JSON format:
{{
    "word_count": <number>,
    "sentence_count": <number>,
    "paragraph_count": <number>,
    "reading_level": "<level>",
    "sentiment": "<positive/negative/neutral>",
    "key_topics": ["<topic1>", "<topic2>"],
    "language": "<detected_language>",
    "tone": "<formal/informal/casual>",
    "summary": "<brief_summary>"
}}"""
            
            payload = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": "You are a text analysis expert. Provide accurate analysis in the requested JSON format."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.3,
                "max_tokens": 1000
            }
            
            response = await self.client.post(
                f"{self.base_url}/chat/completions",
                json=payload
            )
            
            if response.status_code == 200:
                result = response.json()
                analysis_text = result["choices"][0]["message"]["content"].strip()
                
                try:
                    # Try to parse JSON response
                    analysis_data = json.loads(analysis_text)
                    return analysis_data
                except json.JSONDecodeError:
                    # Fallback to basic analysis
                    return self._basic_text_analysis(text)
            else:
                logger.warning("AI text analysis failed, using basic analysis")
                return self._basic_text_analysis(text)
                
        except Exception as e:
            logger.warning(f"AI text analysis error: {str(e)}, using basic analysis")
            return self._basic_text_analysis(text)
    
    def _build_prompt(self, text: str, operation: TextOperation, **kwargs) -> str:
        """Build appropriate prompt for the given operation."""
        
        prompts = {
            TextOperation.SUMMARIZE: f"Please summarize the following text concisely:\n\n{text}",
            TextOperation.IMPROVE: f"Please improve the following text for clarity, grammar, and readability:\n\n{text}",
            TextOperation.TRANSLATE: f"Please translate the following text to {kwargs.get('target_language', 'English')}:\n\n{text}",
            TextOperation.CORRECT: f"Please correct any grammar, spelling, and punctuation errors in the following text:\n\n{text}",
            TextOperation.EXPAND: f"Please expand and elaborate on the following text with more details:\n\n{text}",
            TextOperation.SIMPLIFY: f"Please simplify the following text to make it easier to understand:\n\n{text}",
            TextOperation.ANALYZE: f"Please analyze the following text and provide insights:\n\n{text}"
        }
        
        return prompts.get(operation, f"Please process the following text:\n\n{text}")
    
    def _get_system_prompt(self, operation: TextOperation) -> str:
        """Get system prompt for the given operation."""
        
        system_prompts = {
            TextOperation.SUMMARIZE: "You are an expert at creating concise, accurate summaries that capture the key points of any text.",
            TextOperation.IMPROVE: "You are an expert editor who improves text clarity, grammar, and readability while preserving the original meaning and tone.",
            TextOperation.TRANSLATE: "You are an expert translator who provides accurate, natural translations while preserving context and meaning.",
            TextOperation.CORRECT: "You are an expert proofreader who corrects grammar, spelling, and punctuation errors while maintaining the original style.",
            TextOperation.EXPAND: "You are an expert writer who can elaborate on ideas with relevant details and examples while maintaining coherence.",
            TextOperation.SIMPLIFY: "You are an expert at making complex text easier to understand while preserving all important information.",
            TextOperation.ANALYZE: "You are an expert text analyst who provides detailed insights about content, structure, and meaning."
        }
        
        return system_prompts.get(operation, "You are a helpful AI assistant that processes text according to user requests.")
    
    def _calculate_confidence_score(self, result: Dict[str, Any]) -> float:
        """Calculate confidence score based on AI response."""
        # Simple heuristic based on finish reason and response length
        finish_reason = result["choices"][0].get("finish_reason", "")
        response_length = len(result["choices"][0]["message"]["content"])
        
        if finish_reason == "stop" and response_length > 10:
            return 0.9
        elif finish_reason == "stop":
            return 0.7
        elif finish_reason == "length":
            return 0.6
        else:
            return 0.5
    
    def _basic_text_analysis(self, text: str) -> Dict[str, Any]:
        """Provide basic text analysis without AI."""
        words = text.split()
        sentences = text.split('.')
        paragraphs = text.split('\n\n')
        
        return {
            "word_count": len(words),
            "sentence_count": len([s for s in sentences if s.strip()]),
            "paragraph_count": len([p for p in paragraphs if p.strip()]),
            "character_count": len(text),
            "reading_level": "unknown",
            "sentiment": "neutral",
            "key_topics": [],
            "language": "unknown",
            "tone": "unknown",
            "summary": text[:100] + "..." if len(text) > 100 else text
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Check AI service health."""
        try:
            if not self.client:
                await self.initialize()
            
            # Simple health check with minimal request
            payload = {
                "model": self.model,
                "messages": [{"role": "user", "content": "Hello"}],
                "max_tokens": 5
            }
            
            response = await self.client.post(
                f"{self.base_url}/chat/completions",
                json=payload
            )
            
            return {
                "status": "healthy" if response.status_code == 200 else "unhealthy",
                "status_code": response.status_code,
                "model": self.model,
                "endpoint": self.base_url
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "model": self.model,
                "endpoint": self.base_url
            }


# Global AI service instance
ai_service = AIService()


async def get_ai_service() -> AIService:
    """Dependency function to get AI service instance."""
    if not ai_service.client:
        await ai_service.initialize()
    return ai_service