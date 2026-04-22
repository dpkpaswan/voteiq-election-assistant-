"""
Configuration management for VoteIQ — Election Process Education Assistant
Centralized config with validation and environment-based settings
"""

import os
from typing import List, Optional
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Application configuration with environment-based overrides"""

    # -----------------------------
    # 🔐 API CONFIG
    # -----------------------------
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-1.5-pro")

    # -----------------------------
    # 🇮🇳 ELECTION CONFIG
    # -----------------------------
    ELECTION_COUNTRY: str = os.getenv("ELECTION_COUNTRY", "India")
    DEFAULT_ELECTION_TYPE: str = os.getenv("ELECTION_TYPE", "lok_sabha")
    ELECTION_YEAR: Optional[str] = os.getenv("ELECTION_YEAR")

    # -----------------------------
    # ⚙️ APP MODES
    # -----------------------------
    SUPPORTED_MODES: List[str] = ["guide", "timeline", "quiz"]
    DEFAULT_MODE: str = os.getenv("DEFAULT_MODE", "guide")

    # -----------------------------
    # 🌍 ENVIRONMENT
    # -----------------------------
    ENV: str = os.getenv("ENV", "development")
    DEBUG: bool = ENV == "development"

    # -----------------------------
    # 🛡️ VALIDATION LIMITS
    # -----------------------------
    MIN_INPUT_LENGTH: int = 3
    MAX_INPUT_LENGTH: int = 500

    # -----------------------------
    # 📊 LOGGING
    # -----------------------------
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    # -----------------------------
    # 🔒 SECURITY
    # -----------------------------
    ALLOWED_ORIGINS: List[str] = os.getenv(
        "ALLOWED_ORIGINS",
        "*"
    ).split(",")

    RATE_LIMIT_REQUESTS: int = int(os.getenv("RATE_LIMIT_REQUESTS", "30"))
    RATE_LIMIT_WINDOW: int = int(os.getenv("RATE_LIMIT_WINDOW", "60"))

    # -----------------------------
    # 🔎 FEATURE FLAGS
    # -----------------------------
    ENABLE_AI: bool = bool(GOOGLE_API_KEY)
    ENABLE_QUIZ: bool = True
    ENABLE_TIMELINE: bool = True


# Singleton instance
config = Config()