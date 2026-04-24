"""
Configuration management for VoteIQ — Election Process Education Assistant
Uses Google Cloud Secret Manager in production, env vars in development
"""

import os
import logging
from typing import List, Optional
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)


class Config:
    """
    Application configuration with Google Cloud integration.

    Priority for secrets:
    1. Google Cloud Secret Manager (production on GCP)
    2. Environment variables (development / .env file)
    """

    def __init__(self):
        # Try Secret Manager first, fallback to env vars
        self._secret_manager = None
        self._init_secret_manager()

        # -----------------------------
        # 🔐 API CONFIG (via Secret Manager or env)
        # -----------------------------
        self.GOOGLE_API_KEY: str = self._get_secret("GOOGLE_API_KEY", "")
        self.GEMINI_MODEL: str = self._get_secret("GEMINI_MODEL", "gemini-1.5-pro")

        # -----------------------------
        # ☁️ GOOGLE CLOUD CONFIG
        # -----------------------------
        self.GCP_PROJECT: str = os.getenv("GOOGLE_CLOUD_PROJECT", os.getenv("GCP_PROJECT", ""))
        self.GCS_KNOWLEDGE_BUCKET: str = os.getenv("GCS_KNOWLEDGE_BUCKET", "voteiq-knowledge-base")
        self.ENABLE_CLOUD_LOGGING: bool = os.getenv("ENABLE_CLOUD_LOGGING", "true").lower() == "true"
        self.ENABLE_FIRESTORE: bool = os.getenv("ENABLE_FIRESTORE", "true").lower() == "true"
        self.ENABLE_CLOUD_STORAGE: bool = os.getenv("ENABLE_CLOUD_STORAGE", "true").lower() == "true"

        # Firebase config for frontend analytics
        self.FIREBASE_PROJECT_ID: str = os.getenv("FIREBASE_PROJECT_ID", self.GCP_PROJECT)

        # -----------------------------
        # 🇮🇳 ELECTION CONFIG
        # -----------------------------
        self.ELECTION_COUNTRY: str = os.getenv("ELECTION_COUNTRY", "India")
        self.DEFAULT_ELECTION_TYPE: str = os.getenv("ELECTION_TYPE", "lok_sabha")
        self.ELECTION_YEAR: Optional[str] = os.getenv("ELECTION_YEAR")

        # -----------------------------
        # ⚙️ APP MODES
        # -----------------------------
        self.SUPPORTED_MODES: List[str] = ["guide", "timeline", "quiz"]
        self.DEFAULT_MODE: str = os.getenv("DEFAULT_MODE", "guide")

        # -----------------------------
        # 🌍 ENVIRONMENT
        # -----------------------------
        self.ENV: str = os.getenv("ENV", "development")
        self.DEBUG: bool = self.ENV == "development"

        # -----------------------------
        # 🛡️ VALIDATION LIMITS
        # -----------------------------
        self.MIN_INPUT_LENGTH: int = 3
        self.MAX_INPUT_LENGTH: int = 500

        # -----------------------------
        # 📊 LOGGING
        # -----------------------------
        self.LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

        # -----------------------------
        # 🔒 SECURITY
        # -----------------------------
        self.ALLOWED_ORIGINS: List[str] = os.getenv("ALLOWED_ORIGINS", "*").split(",")
        self.RATE_LIMIT_REQUESTS: int = int(os.getenv("RATE_LIMIT_REQUESTS", "30"))
        self.RATE_LIMIT_WINDOW: int = int(os.getenv("RATE_LIMIT_WINDOW", "60"))

        # -----------------------------
        # 🔎 FEATURE FLAGS
        # -----------------------------
        self.ENABLE_AI: bool = bool(self.GOOGLE_API_KEY)
        self.ENABLE_QUIZ: bool = True
        self.ENABLE_TIMELINE: bool = True

    def _init_secret_manager(self) -> None:
        """Initialize Secret Manager for production environments"""
        try:
            from .services.secret_manager_service import SecretManagerService
            self._secret_manager = SecretManagerService()
        except Exception:
            self._secret_manager = None

    def _get_secret(self, key: str, default: str = "") -> str:
        """Get secret from Secret Manager or env var"""
        # Try Secret Manager
        if self._secret_manager and self._secret_manager.is_available:
            value = self._secret_manager.get_secret(key)
            if value:
                return value

        # Fallback to env var
        return os.getenv(key, default)

    def get_google_services_status(self) -> dict:
        """Return status of all Google Cloud service integrations"""
        return {
            "gemini_ai": self.ENABLE_AI,
            "cloud_logging": self.ENABLE_CLOUD_LOGGING,
            "firestore": self.ENABLE_FIRESTORE,
            "cloud_storage": self.ENABLE_CLOUD_STORAGE,
            "secret_manager": bool(
                self._secret_manager and self._secret_manager.is_available
            ),
            "gcp_project": bool(self.GCP_PROJECT),
        }


# Singleton instance
config = Config()