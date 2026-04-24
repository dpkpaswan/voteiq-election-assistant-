"""
Google Cloud Firestore integration for VoteIQ
Stores chat history, session data, and analytics
"""

import logging
import time
from typing import Dict, List, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class FirestoreService:
    """
    Google Cloud Firestore service for persistent data storage.

    Collections:
    - chat_sessions: User chat history grouped by session
    - analytics: Aggregated usage metrics
    - feedback: User feedback on responses

    Falls back gracefully when Firestore is unavailable.
    """

    def __init__(self):
        self._client = None
        self._available: bool = False
        self._init_client()

    def _init_client(self) -> None:
        """Lazy initialization of Firestore client"""
        try:
            from google.cloud import firestore
            self._client = firestore.Client()
            self._available = True
            logger.info("☁️ Google Cloud Firestore initialized")
        except ImportError:
            logger.warning("google-cloud-firestore not installed, storage disabled")
            self._available = False
        except Exception as e:
            logger.warning(f"Firestore init failed ({e}), storage disabled")
            self._available = False

    @property
    def is_available(self) -> bool:
        """Check if Firestore is connected and available"""
        return self._available and self._client is not None

    # -----------------------------------------
    # 💬 CHAT SESSION STORAGE
    # -----------------------------------------
    def save_chat_message(
        self,
        session_id: str,
        user_message: str,
        assistant_response: str,
        intent: str,
        confidence: float,
        mode: str = "guide"
    ) -> Optional[str]:
        """
        Save a chat message exchange to Firestore.

        Args:
            session_id: Session identifier
            user_message: User's query
            assistant_response: VoteIQ response
            intent: Detected intent category
            confidence: Intent confidence score
            mode: Assistant mode

        Returns:
            Document ID if saved, None if Firestore unavailable
        """
        if not self.is_available:
            return None

        try:
            doc_ref = self._client.collection("chat_sessions").document(session_id)

            # Create or update session document
            doc_ref.set({
                "session_id": session_id,
                "last_active": datetime.utcnow().isoformat(),
                "message_count": self._increment_field(),
            }, merge=True)

            # Add message to subcollection
            message_ref = doc_ref.collection("messages").add({
                "timestamp": datetime.utcnow().isoformat(),
                "user_message": user_message[:500],
                "assistant_response": assistant_response[:2000],
                "intent": intent,
                "confidence": round(confidence, 3),
                "mode": mode,
            })

            logger.debug(f"Chat saved to Firestore: session={session_id}")
            return session_id

        except Exception as e:
            logger.error(f"Firestore save failed: {e}")
            return None

    def _increment_field(self):
        """Get Firestore increment sentinel"""
        try:
            from google.cloud import firestore
            return firestore.Increment(1)
        except Exception:
            return 1

    def get_chat_history(
        self,
        session_id: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Retrieve recent chat history for a session.

        Args:
            session_id: Session identifier
            limit: Maximum messages to retrieve

        Returns:
            List of message dicts ordered by timestamp
        """
        if not self.is_available:
            return []

        try:
            doc_ref = self._client.collection("chat_sessions").document(session_id)
            messages = (
                doc_ref.collection("messages")
                .order_by("timestamp")
                .limit(limit)
                .stream()
            )
            return [msg.to_dict() for msg in messages]

        except Exception as e:
            logger.error(f"Firestore read failed: {e}")
            return []

    # -----------------------------------------
    # 📊 ANALYTICS TRACKING
    # -----------------------------------------
    def track_intent_usage(self, intent: str) -> None:
        """
        Track intent frequency for analytics dashboard.
        Increments a counter for each intent type in Firestore.

        Args:
            intent: Detected intent category
        """
        if not self.is_available:
            return

        try:
            from google.cloud import firestore

            analytics_ref = self._client.collection("analytics").document("intent_counts")
            analytics_ref.set({
                intent: firestore.Increment(1),
                "total_queries": firestore.Increment(1),
                "last_updated": datetime.utcnow().isoformat(),
            }, merge=True)

        except Exception as e:
            logger.error(f"Analytics tracking failed: {e}")

    def track_daily_usage(self) -> None:
        """Track daily API usage metrics"""
        if not self.is_available:
            return

        try:
            from google.cloud import firestore

            today = datetime.utcnow().strftime("%Y-%m-%d")
            daily_ref = self._client.collection("analytics").document(f"daily_{today}")
            daily_ref.set({
                "date": today,
                "request_count": firestore.Increment(1),
                "last_request": datetime.utcnow().isoformat(),
            }, merge=True)

        except Exception as e:
            logger.error(f"Daily usage tracking failed: {e}")

    # -----------------------------------------
    # 📝 FEEDBACK STORAGE
    # -----------------------------------------
    def save_feedback(
        self,
        session_id: str,
        rating: int,
        comment: str = ""
    ) -> bool:
        """
        Save user feedback on a chat session.

        Args:
            session_id: Session identifier
            rating: User rating (1-5)
            comment: Optional feedback comment

        Returns:
            True if saved successfully
        """
        if not self.is_available:
            return False

        try:
            self._client.collection("feedback").add({
                "session_id": session_id,
                "rating": min(5, max(1, rating)),
                "comment": comment[:500],
                "timestamp": datetime.utcnow().isoformat(),
            })
            return True

        except Exception as e:
            logger.error(f"Feedback save failed: {e}")
            return False
