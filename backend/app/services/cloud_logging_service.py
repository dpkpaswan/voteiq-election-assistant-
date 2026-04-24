"""
Google Cloud Logging integration for VoteIQ
Structured logging to Google Cloud Logging with local fallback
"""

import logging
import os
from typing import Optional

logger = logging.getLogger(__name__)


def setup_cloud_logging(log_level: str = "INFO") -> None:
    """
    Initialize Google Cloud Logging if running on GCP.
    Falls back to standard Python logging in local development.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
    """
    try:
        # Only use Cloud Logging if running on GCP or credentials are available
        if os.getenv("GOOGLE_CLOUD_PROJECT") or os.getenv("GCP_PROJECT"):
            import google.cloud.logging as cloud_logging

            client = cloud_logging.Client()
            client.setup_logging(log_level=getattr(logging, log_level, logging.INFO))

            logger.info("☁️ Google Cloud Logging initialized successfully")
        else:
            _setup_local_logging(log_level)

    except ImportError:
        logger.warning("google-cloud-logging not installed, using local logging")
        _setup_local_logging(log_level)

    except Exception as e:
        logger.warning(f"Cloud Logging init failed ({e}), using local fallback")
        _setup_local_logging(log_level)


def _setup_local_logging(log_level: str = "INFO") -> None:
    """Configure structured local logging with a clean format"""
    logging.basicConfig(
        level=getattr(logging, log_level, logging.INFO),
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    logger.info("📋 Local logging initialized")


def log_chat_interaction(
    message: str,
    intent: str,
    confidence: float,
    mode: str,
    session_id: Optional[str] = None,
    response_length: int = 0
) -> None:
    """
    Log a structured chat interaction event.
    When Cloud Logging is active, these appear as structured log entries
    with searchable labels in the GCP Console.

    Args:
        message: User's query (truncated for privacy)
        intent: Detected intent category
        confidence: Intent classification confidence
        mode: Assistant mode (guide/timeline/quiz)
        session_id: Optional session tracking ID
        response_length: Length of the response text
    """
    interaction_logger = logging.getLogger("voteiq.interactions")

    interaction_logger.info(
        "Chat interaction",
        extra={
            "json_fields": {
                "event_type": "chat_interaction",
                "intent": intent,
                "confidence": round(confidence, 3),
                "mode": mode,
                "session_id": session_id or "anonymous",
                "query_length": len(message),
                "query_preview": message[:80] + "..." if len(message) > 80 else message,
                "response_length": response_length,
            }
        }
    )


def log_api_request(
    method: str,
    path: str,
    status_code: int,
    duration_ms: float,
    client_ip: str = "unknown"
) -> None:
    """
    Log structured API request metrics for Cloud Monitoring.

    Args:
        method: HTTP method (GET, POST)
        path: Request path
        status_code: Response status code
        duration_ms: Request duration in milliseconds
        client_ip: Client IP address
    """
    api_logger = logging.getLogger("voteiq.api")

    api_logger.info(
        f"{method} {path} → {status_code}",
        extra={
            "json_fields": {
                "event_type": "api_request",
                "method": method,
                "path": path,
                "status_code": status_code,
                "duration_ms": round(duration_ms, 2),
                "client_ip": client_ip,
            }
        }
    )
