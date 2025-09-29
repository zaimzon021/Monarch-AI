"""
Background service package for the AI Text Assistant Backend.
Contains Windows service implementation and client utilities.
"""

from .listener import (
    BackgroundTextListener,
    WindowsServiceWrapper,
    run_standalone,
    install_service,
    uninstall_service
)

from .client import BackgroundServiceClient, test_background_service

# Only import Windows service class if available
try:
    from .listener import AITextAssistantService
    WINDOWS_SERVICE_AVAILABLE = True
except ImportError:
    AITextAssistantService = None
    WINDOWS_SERVICE_AVAILABLE = False

__all__ = [
    "BackgroundTextListener",
    "WindowsServiceWrapper", 
    "BackgroundServiceClient",
    "run_standalone",
    "install_service",
    "uninstall_service",
    "test_background_service",
    "WINDOWS_SERVICE_AVAILABLE"
]

if WINDOWS_SERVICE_AVAILABLE:
    __all__.append("AITextAssistantService")