"""
Intent classification and routing for VoteIQ (India-focused)
"""

import logging
from typing import List, Tuple
from .gemini_service import GeminiService

logger = logging.getLogger(__name__)


class IntentService:
    """Service for classifying and routing user intents"""

    def __init__(self):
        self.gemini_service = GeminiService()

    # -----------------------------
    # 🧠 MAIN CLASSIFICATION
    # -----------------------------
    def classify(self, message: str) -> Tuple[str, float]:
        """Classify user intent"""

        # Use Gemini if available
        if self.gemini_service.api_key:
            intent, confidence = self.gemini_service.understand_intent(message)

            # ✅ Fallback if low confidence
            if confidence < 0.6:
                fallback_intent = self._keyword_classify(message)
                return fallback_intent, 0.6

            return intent, confidence

        # Fallback keyword-based classification
        return self._keyword_classify(message), 0.6

    # -----------------------------
    # 🔍 KEYWORD CLASSIFIER
    # -----------------------------
    def _keyword_classify(self, message: str) -> str:
        """Keyword-based classification (India-specific)"""

        message_lower = message.lower()

        keywords = {
            "registration": [
                "register", "registration", "voter id", "epic",
                "enroll", "nvsp", "electoral roll"
            ],
            "timeline": [
                "date", "when", "schedule", "timeline",
                "phase", "election dates"
            ],
            "voting": [
                "vote", "voting", "evm", "how to vote",
                "cast vote", "process"
            ],
            "documents": [
                "id", "document", "aadhaar", "passport",
                "driving license", "pan", "proof"
            ],
            "polling": [
                "where to vote", "polling booth", "polling station",
                "location", "booth", "center"
            ],
            "results": [
                "result", "counting", "winner", "who won"
            ]
        }

        for intent, words in keywords.items():
            if any(word in message_lower for word in words):
                return intent

        return "general"

    # -----------------------------
    # 💡 FOLLOW-UP SUGGESTIONS
    # -----------------------------
    def get_follow_up_suggestions(self, intent: str) -> List[str]:
        """Context-aware follow-up suggestions"""

        suggestions = {
            "registration": [
                "How do I check if I'm on the Electoral Roll?",
                "Can I apply for a Voter ID online?",
                "What documents are needed for registration?"
            ],
            "timeline": [
                "How many phases are elections conducted in?",
                "When will voting happen in my state?",
                "What happens after voting?"
            ],
            "voting": [
                "How does the EVM machine work?",
                "What happens inside a polling booth?",
                "Can I vote without a Voter ID?"
            ],
            "documents": [
                "Is Aadhaar enough to vote?",
                "What if I don't have my Voter ID?",
                "Which IDs are accepted at polling booths?"
            ],
            "polling": [
                "How do I find my polling booth?",
                "What are polling hours?",
                "Can I vote in a different booth?"
            ],
            "results": [
                "How are votes counted?",
                "When are results declared?",
                "What is VVPAT?"
            ],
            "general": [
                "How do I register to vote in India?",
                "How does voting work step-by-step?",
                "What documents do I need to vote?"
            ]
        }

        return suggestions.get(intent, suggestions["general"])