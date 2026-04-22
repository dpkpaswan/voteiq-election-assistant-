"""
Service modules for VoteIQ — Election Process Education Assistant
Structured for scalability and domain-driven design
"""

# 🧠 AI / Core Intelligence Services
from .gemini_service import GeminiService
from .intent_service import IntentService
from .assistant_service import AssistantService

# 🗳️ Election Domain Services (India-focused)
from .timeline_service import TimelineService
from .step_service import StepService

# 🔄 Export all services
__all__ = [
    # Core AI
    "GeminiService",
    "IntentService",
    "AssistantService",

    # Election domain
    "TimelineService",
    "StepService"
]