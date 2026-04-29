"""
Centralized constants for VoteIQ — Election Process Education Assistant

Eliminates magic strings and numbers throughout the codebase.
All configurable values should reference these constants.
"""

from typing import Final, FrozenSet


# ─── Application ───
APP_NAME: Final[str] = "VoteIQ"
APP_DESCRIPTION: Final[str] = "Election Process Education Assistant"
APP_VERSION: Final[str] = "2.1.0"
APP_COUNTRY: Final[str] = "India"

# ─── API ───
API_PREFIX: Final[str] = "/api"
DOCS_URL: Final[str] = "/docs"
REDOC_URL: Final[str] = "/redoc"

# ─── Intent Categories ───
INTENT_REGISTRATION: Final[str] = "registration"
INTENT_TIMELINE: Final[str] = "timeline"
INTENT_VOTING: Final[str] = "voting"
INTENT_DOCUMENTS: Final[str] = "documents"
INTENT_POLLING: Final[str] = "polling"
INTENT_RESULTS: Final[str] = "results"
INTENT_GENERAL: Final[str] = "general"

VALID_INTENTS: FrozenSet[str] = frozenset({
    INTENT_REGISTRATION,
    INTENT_TIMELINE,
    INTENT_VOTING,
    INTENT_DOCUMENTS,
    INTENT_POLLING,
    INTENT_RESULTS,
    INTENT_GENERAL,
})

# ─── Assistant Modes ───
MODE_GUIDE: Final[str] = "guide"
MODE_TIMELINE: Final[str] = "timeline"
MODE_QUIZ: Final[str] = "quiz"

VALID_MODES: FrozenSet[str] = frozenset({
    MODE_GUIDE,
    MODE_TIMELINE,
    MODE_QUIZ,
})

# ─── Step IDs ───
STEP_REGISTER: Final[str] = "register"
STEP_VOTING: Final[str] = "voting"
STEP_DOCUMENTS: Final[str] = "documents"
STEP_POLLING: Final[str] = "polling"
STEP_RESULTS: Final[str] = "results"

VALID_STEP_IDS: FrozenSet[str] = frozenset({
    STEP_REGISTER,
    STEP_VOTING,
    STEP_DOCUMENTS,
    STEP_POLLING,
    STEP_RESULTS,
})

# ─── Validation Limits ───
MIN_INPUT_LENGTH: Final[int] = 3
MAX_INPUT_LENGTH: Final[int] = 500
MAX_REPETITION: Final[int] = 6
MIN_ALPHA_CHARS: Final[int] = 2
MAX_SPECIAL_RATIO: Final[float] = 0.5

# ─── Rate Limiting Defaults ───
DEFAULT_RATE_LIMIT_REQUESTS: Final[int] = 30
DEFAULT_RATE_LIMIT_WINDOW: Final[int] = 60

# ─── Gemini AI ───
DEFAULT_GEMINI_MODEL: Final[str] = "gemini-1.5-pro"
DEFAULT_TEMPERATURE: Final[float] = 0.3
DEFAULT_TOP_P: Final[float] = 0.85
DEFAULT_TOP_K: Final[int] = 40
DEFAULT_MAX_TOKENS: Final[int] = 1024
LOW_CONFIDENCE_THRESHOLD: Final[float] = 0.6
DEFAULT_CONFIDENCE: Final[float] = 0.5

# ─── Data Sources ───
KNOWLEDGE_FILE: Final[str] = "election_knowledge.json"
DATA_DIR: Final[str] = "data"

# ─── Indian Election Sources ───
SOURCES_ECI: Final[str] = "Election Commission of India (eci.gov.in)"
SOURCES_NVSP: Final[str] = "National Voters' Service Portal (nvsp.in)"
SOURCES_APP: Final[str] = "Voter Helpline App"

DEFAULT_SOURCES: tuple = (SOURCES_ECI, SOURCES_NVSP, SOURCES_APP)

# ─── Error Messages ───
ERROR_INVALID_INPUT: Final[str] = (
    "Invalid input. Please provide a clear question "
    "(3-500 characters, no special patterns)."
)
ERROR_EMPTY_AFTER_SANITIZE: Final[str] = "Message cannot be empty after sanitization."
ERROR_RATE_LIMIT: Final[str] = "Too many requests. Please wait and try again."
ERROR_INTERNAL: Final[str] = "An unexpected error occurred. Please try again later."

# ─── HTTP Status Codes ───
HTTP_OK: Final[int] = 200
HTTP_BAD_REQUEST: Final[int] = 400
HTTP_NOT_FOUND: Final[int] = 404
HTTP_RATE_LIMITED: Final[int] = 429
HTTP_INTERNAL_ERROR: Final[int] = 500
