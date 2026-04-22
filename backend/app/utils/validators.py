"""
Input validation and sanitization for VoteIQ
Provides security against prompt injection, XSS, and malicious input
"""

import re
import html
from typing import Optional


# -----------------------------
# 🔒 BLOCKED PATTERNS (Security)
# -----------------------------
BLOCKED_PATTERNS = [
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

    Checks:
    - Non-empty and within length limits
    - No excessive character repetition
    - Contains at least some alphabetic characters
    - No prompt injection patterns
    - No HTML/script injection

    Args:
        text: Raw user input string

    Returns:
        True if input is safe and valid, False otherwise
    """

    if not text:
        return False

    text = text.strip()

    # Length check (3-500 characters)
    if len(text) < 3 or len(text) > 500:
        return False

    # Reject excessive repetition (e.g., "aaaaaaa", "??????")
    if re.search(r"(.)\1{6,}", text):
        return False

    # Reject inputs with only symbols (no alphabetic content)
    if re.fullmatch(r"[\W_]+", text):
        return False

    # Must contain at least 2 alphabetic characters
    alpha_count = sum(1 for c in text if c.isalpha())
    if alpha_count < 2:
        return False

    # Check for prompt injection and malicious patterns
    text_lower = text.lower()
    if any(pattern in text_lower for pattern in BLOCKED_PATTERNS):
        return False

    # Reject excessive special character density (> 50% non-alphanumeric)
    special_count = sum(1 for c in text if not c.isalnum() and c != ' ')
    if len(text) > 5 and special_count / len(text) > 0.5:
        return False

    return True


def sanitize_input(text: Optional[str]) -> str:
    """
    Clean and sanitize user input before processing.

    Operations:
    - Strip whitespace
    - Normalize multiple spaces
    - Remove control characters
    - HTML-encode special characters
    - Truncate to max length

    Args:
        text: Raw user input string

    Returns:
        Cleaned and safe string
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
    if len(text) > 500:
        text = text[:500]

    return text.strip()


def validate_message_length(text: str, min_len: int = 3, max_len: int = 500) -> bool:
    """
    Check if message length is within allowed bounds.

    Args:
        text: Input text
        min_len: Minimum allowed length
        max_len: Maximum allowed length

    Returns:
        True if within bounds
    """
    if not text:
        return False
    length = len(text.strip())
    return min_len <= length <= max_len