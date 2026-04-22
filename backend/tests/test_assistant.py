import pytest
from app.services.assistant_service import AssistantService


@pytest.mark.asyncio
async def test_assistant_process_message_fallback():
    """
    Test assistant fallback behavior when AI is unavailable
    """

    service = AssistantService()

    result = await service.process_message(
        "How do I vote in India?",
        "test-session"
    )

    # -----------------------------
    # ✅ STRUCTURE CHECKS
    # -----------------------------
    assert isinstance(result, dict)

    assert "response" in result
    assert "intent" in result
    assert "follow_up_suggestions" in result
    assert "sources" in result

    # -----------------------------
    # 🧠 INTENT VALIDATION
    # -----------------------------
    # Updated intent system
    assert result["intent"] in [
        "voting",
        "registration",
        "timeline",
        "documents",
        "polling",
        "results",
        "general"
    ]

    # -----------------------------
    # 💬 RESPONSE QUALITY
    # -----------------------------
    assert isinstance(result["response"], str)
    assert len(result["response"]) > 20   # meaningful response

    # -----------------------------
    # 💡 FOLLOW-UPS
    # -----------------------------
    assert isinstance(result["follow_up_suggestions"], list)
    assert len(result["follow_up_suggestions"]) > 0

    # -----------------------------
    # 📚 SOURCES
    # -----------------------------
    assert isinstance(result["sources"], list)

    # -----------------------------
    # 🔁 EDGE CASE: EMPTY INPUT
    # -----------------------------
    result_empty = await service.process_message("", "test-session")

    assert "response" in result_empty