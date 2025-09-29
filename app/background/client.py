"""
Client utility for testing the background service.
"""

import asyncio
import json
import socket
from typing import Dict, Any
from datetime import datetime

from app.config.settings import settings
from app.models.requests import BackgroundTextRequest, TextOperation
from app.models.responses import BackgroundTextResponse


class BackgroundServiceClient:
    """Client for communicating with the background service."""
    
    def __init__(self, host: str = "127.0.0.1", port: int = None):
        self.host = host
        self.port = port or settings.background_service_port
    
    async def send_text_request(
        self,
        text: str,
        operation: TextOperation,
        source_application: str = None,
        window_title: str = None,
        user_id: str = None,
        options: Dict[str, Any] = None
    ) -> BackgroundTextResponse:
        """
        Send text modification request to background service.
        
        Args:
            text: Text to modify
            operation: Type of modification
            source_application: Source application name
            window_title: Window title
            user_id: User identifier
            options: Additional options
            
        Returns:
            BackgroundTextResponse: Service response
        """
        # Create request
        request = BackgroundTextRequest(
            text=text,
            operation=operation,
            source_application=source_application,
            window_title=window_title,
            user_id=user_id,
            options=options
        )
        
        # Send request
        try:
            # Connect to service
            reader, writer = await asyncio.open_connection(self.host, self.port)
            
            # Send request data
            request_data = request.json().encode('utf-8')
            writer.write(request_data)
            await writer.drain()
            
            # Read response
            response_data = await reader.read(8192)
            
            # Close connection
            writer.close()
            await writer.wait_closed()
            
            # Parse response
            response_dict = json.loads(response_data.decode('utf-8'))
            return BackgroundTextResponse(**response_dict)
            
        except Exception as e:
            # Return error response
            return BackgroundTextResponse(
                success=False,
                error_message=f"Connection error: {str(e)}",
                processing_time=0.0,
                timestamp=datetime.utcnow()
            )
    
    async def test_connection(self) -> bool:
        """Test connection to background service."""
        try:
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(self.host, self.port),
                timeout=5.0
            )
            writer.close()
            await writer.wait_closed()
            return True
        except Exception:
            return False


# Test functions
async def test_background_service():
    """Test the background service with sample requests."""
    client = BackgroundServiceClient()
    
    print(f"Testing background service at {client.host}:{client.port}")
    
    # Test connection
    if not await client.test_connection():
        print("❌ Cannot connect to background service")
        return
    
    print("✅ Connected to background service")
    
    # Test requests
    test_cases = [
        {
            "text": "This is a test text that needs improvement.",
            "operation": TextOperation.IMPROVE,
            "source_application": "notepad.exe",
            "user_id": "test_user"
        },
        {
            "text": "Please summarize this longer text that contains multiple sentences and ideas that should be condensed into a shorter form.",
            "operation": TextOperation.SUMMARIZE,
            "source_application": "word.exe",
            "user_id": "test_user"
        },
        {
            "text": "Hello world",
            "operation": TextOperation.TRANSLATE,
            "options": {"target_language": "es"},
            "user_id": "test_user"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🧪 Test {i}: {test_case['operation'].value}")
        print(f"   Text: {test_case['text'][:50]}...")
        
        response = await client.send_text_request(**test_case)
        
        if response.success:
            print(f"   ✅ Success (took {response.processing_time:.2f}s)")
            print(f"   Result: {response.modified_text[:100]}...")
        else:
            print(f"   ❌ Failed: {response.error_message}")


if __name__ == "__main__":
    asyncio.run(test_background_service())