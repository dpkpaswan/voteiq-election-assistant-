"""
Chat endpoint for VoteIQ — Election Process Education Assistant
Includes input validation, sanitization, and structured responses
"""

import logging
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from ..models import ChatRequest, ChatResponse, ChatResponseData, ErrorResponse
from ..services.assistant_service import AssistantService
from ..utils.validators import is_valid_input, sanitize_input

router = APIRouter(prefix="/api", tags=["chat"])
logger = logging.getLogger(__name__)

assistant_service = AssistantService()


@router.post(
    "/chat",
    response_model=ChatResponse,
    responses={
        200: {"description": "Successful response", "model": ChatResponse},
        400: {"description": "Invalid input", "model": ErrorResponse},
        429: {"description": "Rate limit exceeded", "model": ErrorResponse},
        500: {"description": "Internal server error", "model": ErrorResponse}
    },
    summary="Chat with VoteIQ Assistant",
    description="Send a message to the AI election education assistant. Supports guide, timeline, and quiz modes."
)
async def chat(request: ChatRequest) -> JSONResponse:
    """
    Send a message to VoteIQ assistant.

    **Supported modes:**
    - `guide` — Step-by-step election guidance
    - `timeline` — Election timeline queries
    - `quiz` — Interactive quiz mode

    **India-specific topics:**
    Registration, voting, documents, polling, results, timelines
    """
    try:
        # ✅ Step 1: Validate input using security validators
        if not is_valid_input(request.message):
            raise HTTPException(
                status_code=400,
                detail="Invalid input. Please provide a clear question (3-500 characters, no special patterns)."
            )

        # ✅ Step 2: Sanitize input before processing
        clean_message = sanitize_input(request.message)

        if not clean_message:
            raise HTTPException(
                status_code=400,
                detail="Message cannot be empty after sanitization."
            )

        # ✅ Step 3: Build context
        user_context = {
            "country": "India",
            "mode": request.mode or "guide",
        }

        # ✅ Step 4: Process message through assistant
        result = await assistant_service.process_message(
            message=clean_message,
            session_id=request.session_id,
            context=user_context
        )

        # ✅ Step 5: Build structured response
        response_payload = {
            "success": True,
            "data": result,
            "context": user_context
        }

        return JSONResponse(content=response_payload)

    except HTTPException:
        raise

    except Exception as e:
        logger.error(f"[CHAT ERROR] {e}", exc_info=True)

        # ❌ Never expose internal error details to client
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": "internal_error",
                "message": "An unexpected error occurred. Please try again later."
            }
        )