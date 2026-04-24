"""
Main assistant orchestrating all services for VoteIQ (India-focused)
Integrates Gemini AI, Firestore storage, and Cloud Logging
"""

import logging
import time
from typing import Dict, List, Any, Optional
from functools import lru_cache

from .gemini_service import GeminiService
from .intent_service import IntentService
from .timeline_service import TimelineService
from .step_service import StepService
from .firestore_service import FirestoreService
from .cloud_logging_service import log_chat_interaction

logger = logging.getLogger(__name__)


class AssistantService:
    """
    VoteIQ — Main Election Education Assistant orchestrator.

    Integrates:
    - Google Gemini AI for intelligent responses
    - Google Cloud Firestore for chat persistence
    - Google Cloud Logging for interaction tracking
    """

    def __init__(self):
        self.gemini_service = GeminiService()
        self.intent_service = IntentService()
        self.timeline_service = TimelineService()
        self.step_service = StepService()
        self.firestore_service = FirestoreService()

    async def process_message(
        self,
        message: str,
        session_id: Optional[str] = None,
        context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Process user message through the full VoteIQ pipeline.

        Pipeline:
        1. Intent Detection (AI + keyword fallback)
        2. Context Building (India-specific)
        3. Response Generation (Gemini Chat or template)
        4. Firestore Persistence (chat history)
        5. Cloud Logging (structured metrics)

        Args:
            message: User's question about Indian elections
            session_id: Optional session tracking ID
            context: Optional context with country and mode

        Returns:
            Structured response dict
        """
        start_time = time.time()
        logger.info(f"Processing message: {message[:50]}...")

        context = context or {"country": "India", "mode": "guide"}
        mode = context.get("mode", "guide")

        # ✅ Step 1: Intent Detection
        intent, confidence = self.intent_service.classify(message)
        logger.info(f"Intent: {intent} (confidence: {confidence})")

        # ✅ Step 2: Context Building (India-specific)
        intent_context = self._get_context_for_intent(intent)

        # ✅ Step 3: Structured Data (serialized for JSON)
        structured_data = self._get_structured_data(mode)

        # ✅ Step 4: Generate Response (Gemini Chat or fallback)
        if self.gemini_service.api_key:
            response_text = self.gemini_service.generate_response(
                message=message,
                intent=intent,
                context=intent_context,
                extra_data=structured_data,
                session_id=session_id,
            )
        else:
            response_text = self._get_template_response(intent)

        # ✅ Step 5: Follow-up Suggestions
        follow_ups = self.intent_service.get_follow_up_suggestions(intent)

        # ✅ Step 6: Sources
        sources = self._get_sources(intent)

        # ✅ Step 7: Persist to Firestore
        if session_id:
            self.firestore_service.save_chat_message(
                session_id=session_id,
                user_message=message,
                assistant_response=response_text,
                intent=intent,
                confidence=confidence,
                mode=mode,
            )
            self.firestore_service.track_intent_usage(intent)
            self.firestore_service.track_daily_usage()

        # ✅ Step 8: Cloud Logging (structured metrics)
        duration_ms = (time.time() - start_time) * 1000
        log_chat_interaction(
            message=message,
            intent=intent,
            confidence=confidence,
            mode=mode,
            session_id=session_id,
            response_length=len(response_text),
        )

        return {
            "response": response_text,
            "intent": intent,
            "confidence": confidence,
            "mode": mode,
            "data": structured_data,
            "follow_up_suggestions": follow_ups[:3],
            "sources": sources,
        }

    # ─── Structured Data ───
    def _get_structured_data(self, mode: str) -> Any:
        """Get mode-based structured data, properly serialized for JSON"""
        if mode == "timeline":
            return self.timeline_service.get_full_timeline()
        elif mode == "guide":
            steps = self.step_service.get_all_steps()
            return [step.model_dump() for step in steps]
        elif mode == "quiz":
            return {"quiz": "Quiz feature coming soon"}
        return None

    # ─── India-Specific Context ───
    def _get_context_for_intent(self, intent: str) -> Dict:
        """India-specific context mapping for intent-based responses"""
        context_map = {
            "registration": {
                "description": "Register in the Electoral Roll via NVSP or Voter Helpline App",
                "requirements": "Indian citizen, 18+, resident of constituency",
                "methods": ["Online (NVSP)", "Mobile App", "Booth Level Officer"]
            },
            "deadlines": {
                "note": "India does not have a single fixed election day.",
                "events": self.timeline_service.get_upcoming_events()
            },
            "voting_methods": {
                "primary": "In-person voting using EVM (Electronic Voting Machine)",
                "other": ["Postal ballot (eligible voters)", "Proxy voting (armed forces)"]
            },
            "requirements": {
                "primary_id": "EPIC (Voter ID Card)",
                "alternative_ids": ["Aadhaar Card", "Passport", "Driving License", "PAN Card"]
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
                "help_topics": ["Voter Registration", "Election Timeline", "Voting Process", "Documents Required", "Polling Booth Info"]
            }
        }
        return context_map.get(intent, context_map["general"])

    # ─── Template Responses (Fallback) ───
    def _get_template_response(self, intent: str) -> str:
        """Template-based fallback responses (India-focused)"""
        templates = {
            "registration": "To vote in India, you must be registered in the Electoral Roll. You can apply online via the NVSP portal, use the Voter Helpline App, or contact your Booth Level Officer.",
            "deadlines": "Election dates in India are not fixed. The Election Commission announces schedules, often in multiple phases.",
            "voting_methods": "Voting in India is primarily done in person using Electronic Voting Machines (EVMs).",
            "requirements": "You should carry your Voter ID (EPIC). If unavailable, use Aadhaar or Passport.",
            "polling_locations": "Find your polling booth on your voter slip or the NVSP website. Polling usually runs 7 AM to 6 PM.",
            "results": "Votes are counted after all phases. Results are declared by the Election Commission of India.",
            "general": "I'm VoteIQ — your election education assistant! I can guide you through voter registration, election timelines, voting steps, and required documents in India."
        }
        return templates.get(intent, templates["general"])

    # ─── Sources ───
    def _get_sources(self, intent: str) -> List[str]:
        """Reliable Indian election information sources"""
        return [
            "Election Commission of India (eci.gov.in)",
            "National Voters' Service Portal (nvsp.in)",
            "Voter Helpline App",
        ]