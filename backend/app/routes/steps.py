"""
Step-by-step guidance endpoints for VoteIQ — Election Process Education Assistant

Provides:
- All step-by-step election guides (5 steps)
- Individual step detail with lazy loading
- Follow-up action suggestions
"""

import logging
from typing import Dict, Any, Callable

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from ..constants import API_PREFIX, VALID_STEP_IDS, HTTP_NOT_FOUND, HTTP_INTERNAL_ERROR
from ..models import StepsResponse, StepDetailResponse, ElectionStep, ErrorResponse
from ..services.step_service import StepService

router = APIRouter(prefix=API_PREFIX, tags=["steps"])
logger = logging.getLogger(__name__)

# Singleton service instance
_step_service = StepService()


@router.get(
    "/steps",
    response_model=StepsResponse,
    responses={500: {"model": ErrorResponse}},
    summary="Get All Step Guides",
    description="Returns all available step-by-step election guides.",
)
async def get_all_steps() -> JSONResponse:
    """Get all available step-by-step election guides (5 steps)."""
    try:
        steps = _step_service.get_all_steps()

        return JSONResponse(content={
            "success": True,
            "count": len(steps),
            "data": [step.model_dump() for step in steps],
        })

    except Exception as e:
        logger.error(f"[STEPS ERROR] {e}", exc_info=True)
        raise HTTPException(
            status_code=HTTP_INTERNAL_ERROR,
            detail="Failed to fetch step guides.",
        )


@router.get(
    "/steps/{step_id}",
    response_model=StepDetailResponse,
    responses={
        404: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
    summary="Get Specific Step Guide",
    description=(
        "Get a specific step-by-step guide. "
        "Available: `register`, `voting`, `documents`, `polling`, `results`"
    ),
)
async def get_step(step_id: str) -> JSONResponse:
    """
    Get a specific step-by-step election guide (India flow).

    Available step_ids:
    - **register** — Voter registration (Electoral Roll, Form 6)
    - **voting** — How to vote using EVM/VVPAT
    - **documents** — Required ID proofs for voting
    - **polling** — Polling booth arrival and process
    - **results** — Vote counting and result declaration
    """
    try:
        # Validate step_id FIRST (avoid unnecessary object creation)
        if step_id not in VALID_STEP_IDS:
            raise HTTPException(
                status_code=HTTP_NOT_FOUND,
                detail=f"Step '{step_id}' not found. Available: {sorted(VALID_STEP_IDS)}",
            )

        # Lazy-load only the requested step (optimized)
        step_builders: Dict[str, Callable[[], ElectionStep]] = {
            "register": _step_service.get_registration_steps,
            "voting": _step_service.get_voting_steps,
            "documents": _step_service.get_document_steps,
            "polling": _step_service.get_polling_steps,
            "results": _step_service.get_results_steps,
        }

        step_data: ElectionStep = step_builders[step_id]()

        return JSONResponse(content={
            "success": True,
            "step_id": step_id,
            "data": step_data.model_dump(),
            "next_options": [
                "Explain more",
                "Show timeline",
                "Start quiz",
                "Go to next step",
            ],
        })

    except HTTPException:
        raise

    except Exception as e:
        logger.error(f"[STEP ERROR] {e}", exc_info=True)
        raise HTTPException(
            status_code=HTTP_INTERNAL_ERROR,
            detail="Failed to fetch step guide.",
        )