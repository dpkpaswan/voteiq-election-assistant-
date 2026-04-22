"""
Gemini LLM integration for VoteIQ — Election Process Education Assistant
Includes safety settings, generation config, and input sanitization
"""

import json
import logging
from typing import Tuple, Dict, Any, Optional
from ..config import config
from ..utils.validators import sanitize_input

logger = logging.getLogger(__name__)

# -----------------------------
# 🛡️ SAFETY SETTINGS
# -----------------------------
SAFETY_SETTINGS = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
]

# -----------------------------
# ⚙️ GENERATION CONFIG
# -----------------------------
GENERATION_CONFIG = {
    "temperature": 0.3,
    "top_p": 0.85,
    "top_k": 40,
    "max_output_tokens": 1024,
}


class GeminiService:
    """Service for interacting with Google Gemini LLM (India-focused election assistant)"""

    def __init__(self):
        self.model_name: str = config.GEMINI_MODEL
        self.api_key: str = config.GOOGLE_API_KEY
        self._client = None

    def _get_client(self):
        """Lazy initialization of Gemini client with safety settings"""
        if self._client is None:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.api_key)
                self._client = genai.GenerativeModel(
                    self.model_name,
                    safety_settings=SAFETY_SETTINGS,
                    generation_config=GENERATION_CONFIG
                )
                logger.info(f"Gemini client initialized with model: {self.model_name}")
            except Exception as e:
                logger.error(f"Gemini init failed: {e}")
                raise
        return self._client

    # -----------------------------
    # 🧠 INTENT UNDERSTANDING
    # -----------------------------
    def understand_intent(self, message: str) -> Tuple[str, float]:
        """Classify user intent using Gemini (India-specific categories)"""

        client = self._get_client()

        # Sanitize user input before sending to LLM
        safe_message = sanitize_input(message)

        prompt = (
            "Classify the user's question about Indian elections into ONE category:\n\n"
            "- registration (Electoral Roll, Voter ID)\n"
            "- timeline (election dates, phases)\n"
            "- voting (how to vote, EVM)\n"
            "- documents (ID proof, EPIC, Aadhaar)\n"
            "- polling (polling booth, location, timing)\n"
            "- results (vote counting, results)\n"
            "- general (anything else)\n\n"
            f'Message: "{safe_message}"\n\n'
            'Output ONLY valid JSON: {"intent": "category", "confidence": 0.0-1.0}'
        )

        try:
            response = client.generate_content(prompt)
            raw = response.text.strip()

            # Clean markdown code fences if present
            if raw.startswith("```"):
                raw = raw.split("```")[1]
                if raw.startswith("json"):
                    raw = raw[4:]
                raw = raw.strip()

            data = json.loads(raw)
            intent = data.get("intent", "general")
            confidence = min(1.0, max(0.0, float(data.get("confidence", 0.7))))

            # Validate intent is in allowed set
            valid_intents = {"registration", "timeline", "voting", "documents", "polling", "results", "general"}
            if intent not in valid_intents:
                intent = "general"

            return intent, confidence

        except Exception as e:
            logger.warning(f"Intent classification failed: {e}")
            return "general", 0.5

    # -----------------------------
    # 💬 RESPONSE GENERATION
    # -----------------------------
    def generate_response(
        self,
        message: str,
        intent: str,
        context: Dict,
        extra_data: Any = None
    ) -> str:
        """Generate intelligent, structured response using Gemini"""

        client = self._get_client()

        # Sanitize user input before sending to LLM
        safe_message = sanitize_input(message)

        # Safely serialize context and extra_data
        context_str = json.dumps(context, default=str, ensure_ascii=False)
        extra_str = json.dumps(extra_data, default=str, ensure_ascii=False) if extra_data else "None"

        prompt = (
            "You are VoteIQ, an interactive assistant explaining Indian elections.\n\n"
            "Rules:\n"
            "- Be simple, clear, and step-by-step\n"
            "- Assume user is a beginner unless the question is advanced\n"
            "- Be neutral and factual\n"
            "- Use Indian context only (Election Commission of India)\n"
            "- Prefer structured explanations (steps, bullets)\n"
            "- DO NOT mention US elections or any other country\n\n"
            f"User Question: {safe_message}\n"
            f"Intent: {intent}\n"
            f"Context: {context_str}\n\n"
            "Output format:\n"
            "- Short explanation\n"
            "- Step-by-step (if applicable)\n"
            "- 1 helpful tip\n"
            "- Ask a follow-up question"
        )

        try:
            response = client.generate_content(prompt)
            return response.text.strip()

        except Exception as e:
            logger.error(f"Generation failed: {e}")
            return self._get_fallback_response(intent)

    # -----------------------------
    # 🛟 FALLBACK RESPONSES
    # -----------------------------
    def _get_fallback_response(self, intent: str) -> str:
        """Template-based fallback when Gemini is unavailable"""

        fallbacks = {
            "registration": "To vote in India, you must be registered in the Electoral Roll. You can apply online via NVSP or through the Voter Helpline App.",
            "timeline": "Election dates in India are announced by the Election Commission and often occur in multiple phases.",
            "voting": "Voting in India is done using Electronic Voting Machines (EVMs) at your assigned polling booth.",
            "documents": "You should carry your Voter ID (EPIC). Alternative IDs like Aadhaar or Passport are also accepted.",
            "polling": "You can find your polling booth on your voter slip or the NVSP website. Polling usually runs from 7 AM to 6 PM.",
            "results": "Votes are counted after polling phases, and results are declared by the Election Commission of India.",
            "general": "I'm VoteIQ — I can help you understand voter registration, election timelines, voting steps, and required documents in India."
        }

        return fallbacks.get(intent, fallbacks["general"])