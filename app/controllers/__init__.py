"""
Controllers package for the AI Text Assistant Backend.
Contains request handling logic and API endpoint controllers.
"""

from .text_controller import TextController, text_controller, get_text_controller

__all__ = [
    "TextController",
    "text_controller", 
    "get_text_controller"
]