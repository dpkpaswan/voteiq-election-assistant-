"""
Input validation and sanitization for VoteIQ

Provides defense-in-depth security against:
- Prompt injection attacks (17+ blocked patterns)
- Cross-site scripting (XSS) via HTML encoding
- Excessive repetition and symbol abuse
- Control character injection
"""

import re
import html
from typing import Optional, List, Final

from ..constants import (
    MIN_INPUT_LENGTH,
    MAX_INPUT_LENGTH,
    MAX_REPETITION,
    MIN_ALPHA_CHARS,
    MAX_SPECIAL_RATIO,
)


# ─── Blocked Patterns (Prompt Injection + XSS) ───
BLOCKED_PATTERNS: Final[List[str]] = [
    "ignore previous instructions",
    "ignore all instructions",
    "system prompt",
    "act as",
    "bypass",
    "jailbreak",
    "pretend you are",
    "forget your instructions",
    "override your",
    "reveal your prompt",
    "what is your system",
    "ignore the above",
    "disregard",
    "<script",
    "javascript:",
    "onerror=",
    "onclick=",
]


def is_valid_input(text: Optional[str]) -> bool:
    """
    Validate user input for safety and usability.

    Performs layered security checks:
    1. Non-empty and within length limits (3-500 chars)
    2. No excessive character repetition (>6 repeats)
    3. Contains at least 2 alphabetic characters
    4. No prompt injection patterns (17+ blocked)
    5. No HTML/script injection
    6. Special character density < 50%

    Args:
        text: Raw user input string

    Returns:
        True if input passes all security and usability checks
    """
    if not text:
        return False

    text = text.strip()

    # Length bounds check
    if len(text) < MIN_INPUT_LENGTH or len(text) > MAX_INPUT_LENGTH:
        return False

    # Reject excessive repetition (e.g., "aaaaaaa", "??????")
    repetition_pattern: str = rf"(.)\1{{{MAX_REPETITION},}}"
    if re.search(repetition_pattern, text):
        return False

    # Reject inputs with only symbols (no alphabetic content)
    if re.fullmatch(r"[\W_]+", text):
        return False

    # Must contain minimum alphabetic characters
    alpha_count: int = sum(1 for c in text if c.isalpha())
    if alpha_count < MIN_ALPHA_CHARS:
        return False

    # Check for prompt injection and malicious patterns
    text_lower: str = text.lower()
    if any(pattern in text_lower for pattern in BLOCKED_PATTERNS):
        return False

    # Reject excessive special character density
    special_count: int = sum(1 for c in text if not c.isalnum() and c != " ")
    if len(text) > 5 and special_count / len(text) > MAX_SPECIAL_RATIO:
        return False

    return True


def sanitize_input(text: Optional[str]) -> str:
    """
    Clean and sanitize user input before processing.

    Operations (in order):
    1. Strip leading/trailing whitespace
    2. Remove control characters (\\x00-\\x1F, \\x7F)
    3. Normalize multiple spaces to single space
    4. HTML-encode special characters (XSS prevention)
    5. Truncate to maximum allowed length

    Args:
        text: Raw user input string

    Returns:
        Cleaned, safe string ready for processing
    """
    if not text:
        return ""

    # Strip whitespace
    text = text.strip()

    # Remove control characters (keep printable + common unicode)
    text = re.sub(r"[\x00-\x1F\x7F]", "", text)

    # Normalize whitespace (multiple spaces/tabs → single space)
    text = re.sub(r"\s+", " ", text)

    # HTML-encode special characters to prevent XSS
    text = html.escape(text, quote=True)

    # Truncate to max length
    if len(text) > MAX_INPUT_LENGTH:
        text = text[:MAX_INPUT_LENGTH]

    return text.strip()


def validate_message_length(
    text: str,
    min_len: int = MIN_INPUT_LENGTH,
    max_len: int = MAX_INPUT_LENGTH,
) -> bool:
    """
    Check if message length is within allowed bounds.

    Args:
        text: Input text to validate
        min_len: Minimum allowed length (default: 3)
        max_len: Maximum allowed length (default: 500)

    Returns:
        True if text length is within [min_len, max_len]
    """
    if not text:
        return False
    length: int = len(text.strip())
    return min_len <= length <= max_len