"""
Chat endpoint for VoteIQ — Election Process Education Assistant

Handles user messages with:
- Input validation and sanitization
- Intent classification via AI
- Multi-turn conversation support
- Structured JSON responses with follow-up suggestions
"""

import logging
from typing import Dict, Any

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from ..constants import (
    API_PREFIX,
    ERROR_INVALID_INPUT,
    ERROR_EMPTY_AFTER_SANITIZE,
    ERROR_INTERNAL,
    APP_COUNTRY,
    MODE_GUIDE,
    HTTP_BAD_REQUEST,
    HTTP_INTERNAL_ERROR,
)
from ..models import ChatRequest, ChatResponse, ChatResponseData, ErrorResponse
from ..services.assistant_service import AssistantService
from ..utils.validators import is_valid_input, sanitize_input

router = APIRouter(prefix=API_PREFIX, tags=["chat"])
logger = logging.getLogger(__name__)

# Singleton service instance (shared across requests)
_assistant_service = AssistantService()


@router.post(
    "/chat",
    response_model=ChatResponse,
    responses={
        200: {"description": "Successful response", "model": ChatResponse},
        400: {"description": "Invalid input", "model": ErrorResponse},
        429: {"description": "Rate limit exceeded", "model": ErrorResponse},
        500: {"description": "Internal server error", "model": ErrorResponse},
    },
    summary="Chat with VoteIQ Assistant",
    description=(
        "Send a message to the AI election education assistant. "
        "Supports guide, timeline, and quiz modes."
    ),
)
async def chat(request: ChatRequest) -> JSONResponse:
    """
    Process user message through the VoteIQ assistant pipeline.

    **Pipeline:**
    1. Input validation (length, pattern, injection checks)
    2. Input sanitization (XSS, control chars, normalization)
    3. Intent detection (Gemini AI + keyword fallback)
    4. Response generation (multi-turn chat or template)
    5. Firestore persistence and Cloud Logging

    **Supported modes:** guide, timeline, quiz
    **India-specific topics:** Registration, voting, documents, polling, results
    """
    try:
        # Step 1: Validate input using security validators
        if not is_valid_input(request.message):
            raise HTTPException(
                status_code=HTTP_BAD_REQUEST,
                detail=ERROR_INVALID_INPUT,
            )

        # Step 2: Sanitize input before processing
        clean_message: str = sanitize_input(request.message)

        if not clean_message:
            raise HTTPException(
                status_code=HTTP_BAD_REQUEST,
                detail=ERROR_EMPTY_AFTER_SANITIZE,
            )

        # Step 3: Build context
        user_context: Dict[str, str] = {
            "country": APP_COUNTRY,
            "mode": request.mode or MODE_GUIDE,
        }

        # Step 4: Process message through assistant
        result: Dict[str, Any] = await _assistant_service.process_message(
            message=clean_message,
            session_id=request.session_id,
            context=user_context,
        )

        # Step 5: Build structured response
        response_payload: Dict[str, Any] = {
            "success": True,
            "data": result,
            "context": user_context,
        }

        return JSONResponse(content=response_payload)

    except HTTPException:
        raise

    except Exception as e:
        logger.error(f"[CHAT ERROR] {e}", exc_info=True)

        # Never expose internal error details to client
        return JSONResponse(
            status_code=HTTP_INTERNAL_ERROR,
            content={
                "success": False,
                "error": "internal_error",
                "message": ERROR_INTERNAL,
            },
        )