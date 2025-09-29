"""
Routes package for the AI Text Assistant Backend.
Contains API endpoint definitions and routing configuration.
"""

from .api import api_router
from .text_routes import router as text_router

__all__ = [
    "api_router",
    "text_router"
]