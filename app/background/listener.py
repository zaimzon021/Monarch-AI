"""
Windows background service listener for system-wide text modification.
"""

import asyncio
import json
import socket
import threading
import time
from datetime import datetime
from typing import Dict, Any, Optional
import structlog

try:
    import win32serviceutil
    import win32service
    import win32event
    import servicemanager
    WINDOWS_SERVICE_AVAILABLE = True
except ImportError:
    # Fallback for non-Windows systems or missing pywin32
    WINDOWS_SERVICE_AVAILABLE = False
    win32serviceutil = None
    win32service = None
    win32event = None
    servicemanager = None

from app.config.settings import settings
from app.models.requests import BackgroundTextRequest, TextOperation
from app.models.responses import BackgroundTextResponse
from app.services.text_service import get_text_service
from app.config.database_init import initialize_database, shutdown_database

logger = structlog.get_logger(__name__)


class BackgroundTextListener:
    """Background listener for text modification requests."""
    
    def __init__(self, host: str = "127.0.0.1", port: int = None):
        self.host = host
        self.port = port or settings.background_service_port
        self.server_socket: Optional[socket.socket] = None
        self.running = False
        self.loop: Optional[asyncio.AbstractEventLoop] = None
        self.server_task: Optional[asyncio.Task] = None
        
    async def start(self):
        """Start the background listener service."""
        try:
            logger.info(f"Starting background listener on {self.host}:{self.port}")
            
            # Initialize database connection
            db_success = await initialize_database()
            if not db_success:
                logger.error("Failed to initialize database for background service")
                return False
            
            # Create server socket
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)
            self.server_socket.setblocking(False)
            
            self.running = True
            
            logger.info(f"Background listener started successfully on {self.host}:{self.port}")
            
            # Start accepting connections
            while self.running:
                try:
                    # Accept connection with timeout
                    self.server_socket.settimeout(1.0)
                    client_socket, address = await asyncio.get_event_loop().sock_accept(self.server_socket)
                    
                    # Handle client in background
                    asyncio.create_task(self._handle_client(client_socket, address))
                    
                except socket.timeout:
                    continue
                except Exception as e:
                    if self.running:
                        logger.error(f"Error accepting connection: {str(e)}")
                    break
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to start background listener: {str(e)}")
            return False
    
    async def stop(self):
        """Stop the background listener service."""
        logger.info("Stopping background listener")
        
        self.running = False
        
        if self.server_socket:
            try:
                self.server_socket.close()
            except Exception as e:
                logger.error(f"Error closing server socket: {str(e)}")
        
        # Shutdown database connection
        await shutdown_database()
        
        logger.info("Background listener stopped")
    
    async def _handle_client(self, client_socket: socket.socket, address: tuple):
        """Handle individual client connection."""
        try:
            logger.debug(f"Handling client connection from {address}")
            
            # Receive data
            data = await asyncio.get_event_loop().sock_recv(client_socket, 4096)
            
            if not data:
                return
            
            # Parse request
            try:
                request_data = json.loads(data.decode('utf-8'))
                request = BackgroundTextRequest(**request_data)
            except (json.JSONDecodeError, ValueError) as e:
                error_response = BackgroundTextResponse(
                    success=False,
                    error_message=f"Invalid request format: {str(e)}",
                    processing_time=0.0,
                    timestamp=datetime.utcnow()
                )
                await self._send_response(client_socket, error_response)
                return
            
            # Process request
            response = await self._process_text_request(request)
            
            # Send response
            await self._send_response(client_socket, response)
            
        except Exception as e:
            logger.error(f"Error handling client {address}: {str(e)}")
            
            error_response = BackgroundTextResponse(
                success=False,
                error_message=f"Processing error: {str(e)}",
                processing_time=0.0,
                timestamp=datetime.utcnow()
            )
            
            try:
                await self._send_response(client_socket, error_response)
            except:
                pass
        finally:
            try:
                client_socket.close()
            except:
                pass
    
    async def _process_text_request(self, request: BackgroundTextRequest) -> BackgroundTextResponse:
        """Process background text modification request."""
        start_time = time.time()
        
        try:
            logger.info(
                "Processing background text request",
                operation=request.operation.value,
                text_length=len(request.text),
                source_application=request.source_application,
                user_id=request.user_id
            )
            
            # Get text service
            text_service = await get_text_service()
            
            # Convert to standard text modification request
            from app.models.requests import TextModificationRequest
            
            modification_request = TextModificationRequest(
                text=request.text,
                operation=request.operation,
                user_id=request.user_id,
                options=request.options
            )
            
            # Process the request
            result = await text_service.process_text_modification(modification_request)
            
            processing_time = time.time() - start_time
            
            logger.info(
                "Background text request processed successfully",
                operation=request.operation.value,
                processing_time=processing_time,
                user_id=request.user_id
            )
            
            return BackgroundTextResponse(
                success=True,
                modified_text=result.modified_text,
                processing_time=processing_time,
                timestamp=datetime.utcnow()
            )
            
        except Exception as e:
            processing_time = time.time() - start_time
            
            logger.error(
                "Background text request failed",
                operation=request.operation.value,
                error=str(e),
                processing_time=processing_time,
                user_id=request.user_id
            )
            
            return BackgroundTextResponse(
                success=False,
                error_message=str(e),
                processing_time=processing_time,
                timestamp=datetime.utcnow()
            )
    
    async def _send_response(self, client_socket: socket.socket, response: BackgroundTextResponse):
        """Send response back to client."""
        try:
            response_data = response.json().encode('utf-8')
            await asyncio.get_event_loop().sock_sendall(client_socket, response_data)
        except Exception as e:
            logger.error(f"Error sending response: {str(e)}")


class WindowsServiceWrapper:
    """Windows service wrapper for the background listener."""
    
    def __init__(self):
        self.listener = BackgroundTextListener()
        self.stop_event = threading.Event()
        
    def start_service(self):
        """Start the service in a new event loop."""
        try:
            # Create new event loop for the service
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # Run the listener
            loop.run_until_complete(self._run_service())
            
        except Exception as e:
            logger.error(f"Service error: {str(e)}")
        finally:
            try:
                loop.close()
            except:
                pass
    
    async def _run_service(self):
        """Run the service until stopped."""
        try:
            # Start the listener
            await self.listener.start()
            
            # Wait for stop signal
            while not self.stop_event.is_set():
                await asyncio.sleep(1)
                
        finally:
            await self.listener.stop()
    
    def stop_service(self):
        """Stop the service."""
        self.stop_event.set()


# Windows Service Class (only available on Windows with pywin32)
if WINDOWS_SERVICE_AVAILABLE:
    class AITextAssistantService(win32serviceutil.ServiceFramework):
        """Windows service for AI Text Assistant background listener."""
        
        _svc_name_ = "AITextAssistantService"
        _svc_display_name_ = "AI Text Assistant Background Service"
        _svc_description_ = "Background service for AI-powered text modification"
        
        def __init__(self, args):
            win32serviceutil.ServiceFramework.__init__(self, args)
            self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
            self.service_wrapper = WindowsServiceWrapper()
            self.service_thread = None
        
        def SvcStop(self):
            """Stop the service."""
            self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
            win32event.SetEvent(self.hWaitStop)
            
            if self.service_wrapper:
                self.service_wrapper.stop_service()
            
            if self.service_thread and self.service_thread.is_alive():
                self.service_thread.join(timeout=10)
        
        def SvcDoRun(self):
            """Run the service."""
            servicemanager.LogMsg(
                servicemanager.EVENTLOG_INFORMATION_TYPE,
                servicemanager.PYS_SERVICE_STARTED,
                (self._svc_name_, '')
            )
            
            # Start service in separate thread
            self.service_thread = threading.Thread(
                target=self.service_wrapper.start_service
            )
            self.service_thread.start()
            
            # Wait for stop event
            win32event.WaitForSingleObject(self.hWaitStop, win32event.INFINITE)
            
            servicemanager.LogMsg(
                servicemanager.EVENTLOG_INFORMATION_TYPE,
                servicemanager.PYS_SERVICE_STOPPED,
                (self._svc_name_, '')
            )


# Standalone runner for development/testing
async def run_standalone():
    """Run the background listener as a standalone application."""
    listener = BackgroundTextListener()
    
    try:
        await listener.start()
    except KeyboardInterrupt:
        logger.info("Received interrupt signal")
    finally:
        await listener.stop()


def install_service():
    """Install the Windows service."""
    if not WINDOWS_SERVICE_AVAILABLE:
        print("Windows service functionality not available (pywin32 not installed)")
        return False
    
    try:
        win32serviceutil.InstallService(
            AITextAssistantService._svc_reg_class_,
            AITextAssistantService._svc_name_,
            AITextAssistantService._svc_display_name_,
            description=AITextAssistantService._svc_description_
        )
        print(f"Service '{AITextAssistantService._svc_display_name_}' installed successfully")
        return True
    except Exception as e:
        print(f"Failed to install service: {str(e)}")
        return False


def uninstall_service():
    """Uninstall the Windows service."""
    if not WINDOWS_SERVICE_AVAILABLE:
        print("Windows service functionality not available (pywin32 not installed)")
        return False
    
    try:
        win32serviceutil.RemoveService(AITextAssistantService._svc_name_)
        print(f"Service '{AITextAssistantService._svc_display_name_}' uninstalled successfully")
        return True
    except Exception as e:
        print(f"Failed to uninstall service: {str(e)}")
        return False


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "install":
            install_service()
        elif command == "uninstall":
            uninstall_service()
        elif command == "standalone":
            asyncio.run(run_standalone())
        elif WINDOWS_SERVICE_AVAILABLE:
            # Handle Windows service commands
            win32serviceutil.HandleCommandLine(AITextAssistantService)
        else:
            print("Windows service functionality not available")
    else:
        # Run standalone by default
        print("Running in standalone mode (use Ctrl+C to stop)")
        asyncio.run(run_standalone())