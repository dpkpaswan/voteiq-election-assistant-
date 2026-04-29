"""
Intent classification and routing for VoteIQ (India-focused)

Provides two-tier classification:
1. Google Gemini AI (primary — high accuracy)
2. Keyword-based fallback (when AI unavailable or low confidence)
"""

import logging
from typing import List, Tuple, Dict, Final

from ..constants import (
    INTENT_REGISTRATION,
    INTENT_TIMELINE,
    INTENT_VOTING,
    INTENT_DOCUMENTS,
    INTENT_POLLING,
    INTENT_RESULTS,
    INTENT_GENERAL,
    LOW_CONFIDENCE_THRESHOLD,
    DEFAULT_CONFIDENCE,
)
from .gemini_service import GeminiService

logger = logging.getLogger(__name__)


# ─── Keyword → Intent Mapping (India-specific) ───
KEYWORD_MAP: Final[Dict[str, List[str]]] = {
    INTENT_REGISTRATION: [
        "register", "registration", "voter id", "epic",
        "enroll", "nvsp", "electoral roll", "form 6",
    ],
    INTENT_TIMELINE: [
        "date", "when", "schedule", "timeline",
        "phase", "election dates", "calendar",
    ],
    INTENT_VOTING: [
        "vote", "voting", "evm", "how to vote",
        "cast vote", "process", "vvpat",
    ],
    INTENT_DOCUMENTS: [
        "id", "document", "aadhaar", "passport",
        "driving license", "pan", "proof", "epic card",
    ],
    INTENT_POLLING: [
        "where to vote", "polling booth", "polling station",
        "location", "booth", "center", "queue",
    ],
    INTENT_RESULTS: [
        "result", "counting", "winner", "who won",
        "declared", "tally",
    ],
}

# ─── Follow-up Suggestions per Intent ───
FOLLOW_UP_MAP: Final[Dict[str, List[str]]] = {
    INTENT_REGISTRATION: [
        "How do I check if I'm on the Electoral Roll?",
        "Can I apply for a Voter ID online?",
        "What documents are needed for registration?",
    ],
    INTENT_TIMELINE: [
        "How many phases are elections conducted in?",
        "When will voting happen in my state?",
        "What happens after voting?",
    ],
    INTENT_VOTING: [
        "How does the EVM machine work?",
        "What happens inside a polling booth?",
        "Can I vote without a Voter ID?",
    ],
    INTENT_DOCUMENTS: [
        "Is Aadhaar enough to vote?",
        "What if I don't have my Voter ID?",
        "Which IDs are accepted at polling booths?",
    ],
    INTENT_POLLING: [
        "How do I find my polling booth?",
        "What are polling hours?",
        "Can I vote in a different booth?",
    ],
    INTENT_RESULTS: [
        "How are votes counted?",
        "When are results declared?",
        "What is VVPAT?",
    ],
    INTENT_GENERAL: [
        "How do I register to vote in India?",
        "How does voting work step-by-step?",
        "What documents do I need to vote?",
    ],
}


class IntentService:
    """
    Two-tier intent classification service for VoteIQ.

    Classification pipeline:
    1. Gemini AI classification (if API key available)
    2. Confidence check (threshold: 0.6)
    3. Keyword-based fallback (if AI unavailable or low confidence)
    """

    def __init__(self) -> None:
        self._gemini_service = GeminiService()

    def classify(self, message: str) -> Tuple[str, float]:
        """
        Classify user intent using AI with keyword fallback.

        Args:
            message: User's election-related question

        Returns:
            Tuple of (intent_category, confidence_score)
        """
        # Primary: Use Gemini AI if available
        if self._gemini_service.api_key:
            intent, confidence = self._gemini_service.understand_intent(message)

            # Fallback if low confidence
            if confidence < LOW_CONFIDENCE_THRESHOLD:
                fallback_intent: str = self._keyword_classify(message)
                return fallback_intent, LOW_CONFIDENCE_THRESHOLD

            return intent, confidence

        # Secondary: Keyword-based classification
        return self._keyword_classify(message), DEFAULT_CONFIDENCE

    def _keyword_classify(self, message: str) -> str:
        """
        Keyword-based intent classification (India-specific).

        Scans message for known election terminology and maps
        to the most relevant intent category.

        Args:
            message: User's question text

        Returns:
            Intent category string
        """
        message_lower: str = message.lower()

        for intent, keywords in KEYWORD_MAP.items():
            if any(keyword in message_lower for keyword in keywords):
                return intent

        return INTENT_GENERAL

    def get_follow_up_suggestions(self, intent: str) -> List[str]:
        """
        Get context-aware follow-up question suggestions.

        Args:
            intent: Current detected intent category

        Returns:
            List of 3 suggested follow-up questions
        """
        return FOLLOW_UP_MAP.get(intent, FOLLOW_UP_MAP[INTENT_GENERAL])