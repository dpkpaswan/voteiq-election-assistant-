"""
Test suite for VoteIQ — Election Process Education Assistant 🇮🇳

Contains unit and integration tests for:
- API endpoints (test_api.py)
- Services (test_assistant.py, test_steps.py)
- Intent classification (test_intent.py)
- Timeline service (test_timeline.py)
- Input validation & security (test_validators.py)

Run tests using:
    pytest tests/ -v
"""

__all__ = [
    "test_api",
    "test_assistant",
    "test_intent",
    "test_timeline",
    "test_steps",
    "test_validators"
]