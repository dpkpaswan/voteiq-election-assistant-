"""
Route handlers for VoteIQ — Election Process Education Assistant
Aligned with Election Commission of India workflows
"""

# Core interaction routes
from .chat import router as chat_router
from .timeline import router as timeline_router
from .steps import router as steps_router

# Export all routers
__all__ = [
    "chat_router",
    "timeline_router",
    "steps_router"
]