"""
Google Gemini AI integration for VoteIQ — Election Process Education Assistant

Features:
- Multi-turn chat sessions via Gemini Chat API
- Intent classification with structured JSON output
- Response generation with India-specific system prompt
- Safety settings and generation config
- Semantic similarity via embeddings (when available)
- Input sanitization before LLM calls
"""

import json
import logging
from typing import Tuple, Dict, Any, Optional, List
from functools import lru_cache

from ..config import config
from ..utils.validators import sanitize_input

logger = logging.getLogger(__name__)

# ─── VoteIQ System Prompt (India-focused) ───
SYSTEM_INSTRUCTION = (
    "You are VoteIQ, an interactive AI assistant that educates Indian citizens "
    "about the election process.\n\n"
    "Rules:\n"
    "1. Be simple, clear, and step-by-step\n"
    "2. Assume user is a beginner unless the question is advanced\n"
    "3. Be neutral, factual, and non-partisan\n"
    "4. Use only Indian context (Election Commission of India)\n"
    "5. Prefer structured explanations (steps, bullets, numbered lists)\n"
    "6. DO NOT mention elections of any other country\n"
    "7. End with a helpful follow-up question\n"
    "8. Always cite sources like eci.gov.in or nvsp.in when relevant\n"
)

# ─── Safety Settings ───
SAFETY_SETTINGS = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
]

# ─── Generation Config ───
GENERATION_CONFIG = {
    "temperature": 0.3,
    "top_p": 0.85,
    "top_k": 40,
    "max_output_tokens": 1024,
}


class GeminiService:
    """
    Google Gemini AI service for VoteIQ.

    Provides:
    - Multi-turn chat sessions with conversation history
    - Intent classification (JSON structured output)
    - Response generation with India-specific context
    - Text embeddings for semantic search (optional)
    """

    def __init__(self):
        self.model_name: str = config.GEMINI_MODEL
        self.api_key: str = config.GOOGLE_API_KEY
        self._client = None
        self._chat_sessions: Dict[str, Any] = {}
        self._embedding_model = None

    def _get_client(self):
        """Lazy initialization of Gemini model with system instruction"""
        if self._client is None:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.api_key)

                self._client = genai.GenerativeModel(
                    self.model_name,
                    safety_settings=SAFETY_SETTINGS,
                    generation_config=GENERATION_CONFIG,
                    system_instruction=SYSTEM_INSTRUCTION,
                )
                logger.info(f"✅ Gemini model initialized: {self.model_name}")
            except Exception as e:
                logger.error(f"Gemini init failed: {e}")
                raise
        return self._client

    # ─────────────────────────────────
    # 💬 CHAT SESSIONS (Multi-turn)
    # ─────────────────────────────────
    def get_or_create_chat(self, session_id: str):
        """
        Get or create a Gemini Chat session for multi-turn conversation.
        Chat sessions maintain history for contextual responses.

        Args:
            session_id: Unique session identifier

        Returns:
            Gemini Chat session object
        """
        if session_id not in self._chat_sessions:
            client = self._get_client()
            self._chat_sessions[session_id] = client.start_chat(history=[])
            logger.info(f"New Gemini chat session created: {session_id}")

        return self._chat_sessions[session_id]

    def clear_chat_session(self, session_id: str) -> None:
        """Remove a chat session from memory"""
        if session_id in self._chat_sessions:
            del self._chat_sessions[session_id]
            logger.info(f"Chat session cleared: {session_id}")

    # ─────────────────────────────────
    # 🧠 INTENT CLASSIFICATION
    # ─────────────────────────────────
    def understand_intent(self, message: str) -> Tuple[str, float]:
        """
        Classify user intent using Gemini (India-specific categories).

        Categories: registration, timeline, voting, documents, polling, results, general

        Args:
            message: User's question

        Returns:
            Tuple of (intent_category, confidence_score)
        """
        client = self._get_client()
        safe_message = sanitize_input(message)

        prompt = (
            "Classify this Indian election question into ONE category:\n\n"
            "Categories:\n"
            "- registration (Electoral Roll, Voter ID, Form 6)\n"
            "- timeline (election dates, phases, schedule)\n"
            "- voting (how to vote, EVM, VVPAT, booth process)\n"
            "- documents (ID proof, EPIC, Aadhaar for voting)\n"
            "- polling (polling booth, location, timing, queue)\n"
            "- results (vote counting, results declaration)\n"
            "- general (anything else)\n\n"
            f'Question: "{safe_message}"\n\n'
            'Respond ONLY with valid JSON: {"intent": "category", "confidence": 0.0-1.0}'
        )

        try:
            response = client.generate_content(prompt)
            raw = response.text.strip()

            # Clean markdown code fences
            if raw.startswith("```"):
                raw = raw.split("```")[1]
                if raw.startswith("json"):
                    raw = raw[4:]
                raw = raw.strip()

            data = json.loads(raw)
            intent = data.get("intent", "general")
            confidence = min(1.0, max(0.0, float(data.get("confidence", 0.7))))

            valid_intents = {"registration", "timeline", "voting", "documents", "polling", "results", "general"}
            if intent not in valid_intents:
                intent = "general"

            return intent, confidence

        except Exception as e:
            logger.warning(f"Intent classification failed: {e}")
            return "general", 0.5

    # ─────────────────────────────────
    # 💬 RESPONSE GENERATION
    # ─────────────────────────────────
    def generate_response(
        self,
        message: str,
        intent: str,
        context: Dict,
        extra_data: Any = None,
        session_id: Optional[str] = None
    ) -> str:
        """
        Generate response using Gemini Chat (multi-turn) or single-shot.

        Uses chat sessions when session_id is provided for contextual
        follow-up conversations.

        Args:
            message: User's question
            intent: Detected intent category
            context: India-specific context data
            extra_data: Additional structured data
            session_id: Optional session ID for multi-turn chat

        Returns:
            Generated response text
        """
        safe_message = sanitize_input(message)
        context_str = json.dumps(context, default=str, ensure_ascii=False)

        user_prompt = (
            f"User Question: {safe_message}\n"
            f"Detected Intent: {intent}\n"
            f"Context: {context_str}\n\n"
            "Provide:\n"
            "1. A clear, concise explanation\n"
            "2. Step-by-step instructions (if applicable)\n"
            "3. One helpful tip\n"
            "4. A follow-up question to keep the conversation going"
        )

        try:
            # Use multi-turn chat if session_id provided
            if session_id:
                chat = self.get_or_create_chat(session_id)
                response = chat.send_message(user_prompt)
            else:
                client = self._get_client()
                response = client.generate_content(user_prompt)

            return response.text.strip()

        except Exception as e:
            logger.error(f"Generation failed: {e}")
            return self._get_fallback_response(intent)

    # ─────────────────────────────────
    # 🔍 TEXT EMBEDDINGS
    # ─────────────────────────────────
    def get_embedding(self, text: str) -> Optional[List[float]]:
        """
        Generate text embedding using Gemini Embedding model.
        Useful for semantic search over the knowledge base.

        Args:
            text: Text to embed

        Returns:
            Embedding vector (list of floats) or None
        """
        try:
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)

            result = genai.embed_content(
                model="models/embedding-001",
                content=text,
                task_type="retrieval_document"
            )

            return result.get("embedding")

        except Exception as e:
            logger.warning(f"Embedding generation failed: {e}")
            return None

    @lru_cache(maxsize=64)
    def get_cached_embedding(self, text: str) -> Optional[tuple]:
        """Cached version of get_embedding (returns tuple for hashability)"""
        embedding = self.get_embedding(text)
        return tuple(embedding) if embedding else None

    # ─────────────────────────────────
    # 🛟 FALLBACK RESPONSES
    # ─────────────────────────────────
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