"""
Main assistant orchestrating all services for VoteIQ (India-focused)
Handles intent detection, context building, response generation, and structured data
"""

import logging
from typing import Dict, List, Any
from functools import lru_cache

from .gemini_service import GeminiService
from .intent_service import IntentService
from .timeline_service import TimelineService
from .step_service import StepService

logger = logging.getLogger(__name__)


class AssistantService:
    """VoteIQ — Main Election Education Assistant orchestrator"""

    def __init__(self):
        self.gemini_service = GeminiService()
        self.intent_service = IntentService()
        self.timeline_service = TimelineService()
        self.step_service = StepService()

    async def process_message(
        self,
        message: str,
        session_id: str = None,
        context: Dict = None
    ) -> Dict[str, Any]:
        """
        Process user message and return assistant response.

        Args:
            message: User's question about Indian elections
            session_id: Optional session tracking ID
            context: Optional context with country and mode

        Returns:
            Structured response dict with response text, intent, suggestions, and sources
        """

        logger.info(f"Processing message: {message[:50]}...")

        context = context or {"country": "India", "mode": "guide"}

        # ✅ Step 1: Intent Detection
        intent, confidence = self.intent_service.classify(message)
        logger.info(f"Intent: {intent} (confidence: {confidence})")

        # ✅ Step 2: Fetch contextual data
        intent_context = self._get_context_for_intent(intent)

        # ✅ Step 3: Mode-based structured data (serialized for JSON safety)
        structured_data = self._get_structured_data(context.get("mode", "guide"))

        # ✅ Step 4: Generate response (AI or fallback)
        if self.gemini_service.api_key:
            response_text = self.gemini_service.generate_response(
                message=message,
                intent=intent,
                context=intent_context,
                extra_data=structured_data
            )
        else:
            response_text = self._get_template_response(intent)

        # ✅ Step 5: Follow-ups (interactive)
        follow_ups = self.intent_service.get_follow_up_suggestions(intent)

        # ✅ Step 6: Sources (India-specific)
        sources = self._get_sources(intent)

        return {
            "response": response_text,
            "intent": intent,
            "confidence": confidence,
            "mode": context.get("mode"),
            "data": structured_data,
            "follow_up_suggestions": follow_ups[:3],
            "sources": sources
        }

    # -----------------------------
    # 📦 STRUCTURED DATA (SERIALIZED)
    # -----------------------------
    def _get_structured_data(self, mode: str) -> Any:
        """Get mode-based structured data, properly serialized for JSON"""

        if mode == "timeline":
            return self.timeline_service.get_full_timeline()

        elif mode == "guide":
            # Serialize Pydantic models to dicts for JSON compatibility
            steps = self.step_service.get_all_steps()
            return [step.model_dump() for step in steps]

        elif mode == "quiz":
            return {"quiz": "Quiz feature coming soon"}

        return None

    # -----------------------------
    # 🧠 CONTEXT (INDIA-SPECIFIC)
    # -----------------------------
    def _get_context_for_intent(self, intent: str) -> Dict:
        """India-specific context mapping for intent-based responses"""

        context_map = {
            "registration": {
                "description": "Register in the Electoral Roll via NVSP or Voter Helpline App",
                "requirements": "Indian citizen, 18+, resident of constituency",
                "methods": ["Online (NVSP)", "Mobile App", "Booth Level Officer"]
            },
            "deadlines": {
                "note": "India does not have a single fixed election day. Dates are announced by the Election Commission.",
                "events": self.timeline_service.get_upcoming_events()
            },
            "voting_methods": {
                "primary": "In-person voting using EVM (Electronic Voting Machine)",
                "other": ["Postal ballot (eligible voters)", "Proxy voting (armed forces)"]
            },
            "requirements": {
                "primary_id": "EPIC (Voter ID Card)",
                "alternative_ids": [
                    "Aadhaar Card",
                    "Passport",
                    "Driving License",
                    "PAN Card"
                ]
            },
            "polling_locations": {
                "where_to_find": "Voter Slip or NVSP website",
                "hours": "Typically 7 AM – 6 PM",
                "machine": "EVM with VVPAT"
            },
            "results": {
                "process": "Votes counted centrally after polling phases",
                "announcement": "Results declared by Election Commission"
            },
            "general": {
                "help_topics": [
                    "Voter Registration",
                    "Election Timeline",
                    "Voting Process",
                    "Documents Required",
                    "Polling Booth Info"
                ]
            }
        }

        return context_map.get(intent, context_map["general"])

    # -----------------------------
    # 📝 TEMPLATE RESPONSES (FALLBACK)
    # -----------------------------
    def _get_template_response(self, intent: str) -> str:
        """Template-based fallback responses (India-focused)"""

        templates = {
            "registration": (
                "To vote in India, you must be registered in the Electoral Roll. "
                "You can apply online via the NVSP portal, use the Voter Helpline App, "
                "or contact your Booth Level Officer."
            ),
            "deadlines": (
                "Election dates in India are not fixed. The Election Commission announces "
                "schedules, often in multiple phases. Check upcoming events for details."
            ),
            "voting_methods": (
                "Voting in India is primarily done in person using Electronic Voting Machines (EVMs). "
                "Some voters are eligible for postal ballots."
            ),
            "requirements": (
                "You should carry your Voter ID (EPIC). If unavailable, you can use "
                "alternative government-issued IDs like Aadhaar or Passport."
            ),
            "polling_locations": (
                "You can find your polling booth on your voter slip or through the NVSP website. "
                "Polling usually runs from 7 AM to 6 PM."
            ),
            "results": (
                "Votes are counted after all phases of polling. "
                "Results are declared by the Election Commission of India."
            ),
            "general": (
                "I'm VoteIQ — your election education assistant! I can guide you through "
                "voter registration, election timelines, voting steps, and required documents "
                "in India. What would you like to know?"
            )
        }

        return templates.get(intent, templates["general"])

    # -----------------------------
    # 📚 SOURCES (INDIA-SPECIFIC)
    # -----------------------------
    def _get_sources(self, intent: str) -> List[str]:
        """Reliable Indian election information sources"""

        return [
            "Election Commission of India (eci.gov.in)",
            "National Voters' Service Portal (nvsp.in)",
            "Voter Helpline App"
        ]