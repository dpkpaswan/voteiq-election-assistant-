"""
Service layer for VoteIQ — Election Process Education Assistant

Google Cloud Services:
- GeminiService: Google Gemini AI (chat, intent classification, embeddings)
- FirestoreService: Google Cloud Firestore (chat history, analytics)
- CloudLoggingService: Google Cloud Logging (structured logs)
- SecretManagerService: Google Cloud Secret Manager (secure credentials)
- CloudStorageService: Google Cloud Storage (knowledge base)

Application Services:
- AssistantService: Main orchestrator
- IntentService: Intent classification (AI + keyword fallback)
- TimelineService: Election timeline data
- StepService: Step-by-step guides
"""

from .gemini_service import GeminiService
from .intent_service import IntentService
from .timeline_service import TimelineService
from .step_service import StepService
from .assistant_service import AssistantService
from .firestore_service import FirestoreService
from .cloud_logging_service import setup_cloud_logging, log_chat_interaction, log_api_request
from .secret_manager_service import SecretManagerService
from .cloud_storage_service import CloudStorageService

__all__ = [
    # Google Cloud Services
    "GeminiService",
    "FirestoreService",
    "SecretManagerService",
    "CloudStorageService",
    "setup_cloud_logging",
    "log_chat_interaction",
    "log_api_request",
    # Application Services
    "AssistantService",
    "IntentService",
    "TimelineService",
    "StepService",
]