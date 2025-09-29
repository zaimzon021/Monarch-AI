"""
Mock AI service for testing and development.
"""

import asyncio
import random
from typing import Dict, Any
from datetime import datetime

from app.models.requests import TextOperation


class MockAIService:
    """Mock AI service that simulates AI operations for testing."""
    
    def __init__(self, simulate_delay: bool = True, failure_rate: float = 0.0):
        self.simulate_delay = simulate_delay
        self.failure_rate = failure_rate  # 0.0 to 1.0
        self.model = "mock-ai-model"
    
    async def initialize(self):
        """Initialize mock service (no-op)."""
        pass
    
    async def close(self):
        """Close mock service (no-op)."""
        pass
    
    async def modify_text(self, text: str, operation: TextOperation, **kwargs) -> Dict[str, Any]:
        """
        Mock text modification that simulates AI processing.
        
        Args:
            text: Text to modify
            operation: Type of modification
            **kwargs: Additional options
            
        Returns:
            Dict containing mock modified text and metadata
        """
        # Simulate processing delay
        if self.simulate_delay:
            delay = random.uniform(0.5, 2.0)
            await asyncio.sleep(delay)
        
        # Simulate random failures
        if random.random() < self.failure_rate:
            from app.middlewares.error_handler import AIServiceError
            raise AIServiceError("Mock AI service failure", status_code=502, is_retryable=True)
        
        # Generate mock response based on operation
        modified_text = self._generate_mock_response(text, operation, **kwargs)
        
        return {
            "modified_text": modified_text,
            "original_text": text,
            "operation": operation.value,
            "processing_time": random.uniform(0.5, 2.0),
            "ai_model_used": self.model,
            "tokens_used": random.randint(50, 200),
            "prompt_tokens": random.randint(20, 100),
            "completion_tokens": random.randint(30, 100),
            "confidence_score": random.uniform(0.7, 0.95),
            "metadata": {
                "finish_reason": "stop",
                "model": self.model,
                "mock": True
            }
        }
    
    async def analyze_text(self, text: str) -> Dict[str, Any]:
        """Mock text analysis."""
        if self.simulate_delay:
            await asyncio.sleep(random.uniform(0.3, 1.0))
        
        words = text.split()
        sentences = text.split('.')
        
        return {
            "word_count": len(words),
            "sentence_count": len([s for s in sentences if s.strip()]),
            "paragraph_count": len(text.split('\n\n')),
            "character_count": len(text),
            "reading_level": random.choice(["Elementary", "Middle School", "High School", "College"]),
            "sentiment": random.choice(["positive", "negative", "neutral"]),
            "key_topics": self._extract_mock_topics(text),
            "language": "English",
            "tone": random.choice(["formal", "informal", "casual", "professional"]),
            "summary": text[:50] + "..." if len(text) > 50 else text
        }
    
    def _generate_mock_response(self, text: str, operation: TextOperation, **kwargs) -> str:
        """Generate mock response based on operation type."""
        
        responses = {
            TextOperation.SUMMARIZE: f"[SUMMARY] {text[:100]}...",
            TextOperation.IMPROVE: f"[IMPROVED] {text.replace('.', '. Furthermore,').replace(',', ', additionally,')}",
            TextOperation.TRANSLATE: f"[TRANSLATED to {kwargs.get('target_language', 'Spanish')}] {text}",
            TextOperation.CORRECT: f"[CORRECTED] {text.replace('teh', 'the').replace('recieve', 'receive')}",
            TextOperation.EXPAND: f"[EXPANDED] {text} This provides additional context and detail to enhance understanding.",
            TextOperation.SIMPLIFY: f"[SIMPLIFIED] {text.replace('utilize', 'use').replace('demonstrate', 'show')}",
            TextOperation.ANALYZE: f"[ANALYSIS] This text contains {len(text.split())} words and discusses various topics."
        }
        
        return responses.get(operation, f"[PROCESSED] {text}")
    
    def _extract_mock_topics(self, text: str) -> list:
        """Extract mock topics from text."""
        words = text.lower().split()
        
        # Simple keyword-based topic extraction
        topic_keywords = {
            "technology": ["computer", "software", "digital", "internet", "tech"],
            "business": ["company", "market", "sales", "profit", "business"],
            "education": ["learn", "study", "school", "education", "student"],
            "health": ["health", "medical", "doctor", "treatment", "wellness"],
            "science": ["research", "study", "experiment", "data", "analysis"]
        }
        
        detected_topics = []
        for topic, keywords in topic_keywords.items():
            if any(keyword in words for keyword in keywords):
                detected_topics.append(topic)
        
        return detected_topics[:3]  # Return max 3 topics
    
    async def health_check(self) -> Dict[str, Any]:
        """Mock health check."""
        return {
            "status": "healthy",
            "status_code": 200,
            "model": self.model,
            "endpoint": "mock://ai-service",
            "mock": True
        }


# Mock service instance
mock_ai_service = MockAIService()