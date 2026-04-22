"""
Step-by-step guidance endpoints for VoteIQ
Optimized with lazy step loading and proper response models
"""

import logging
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from ..models import StepsResponse, StepDetailResponse, ErrorResponse
from ..services.step_service import StepService

router = APIRouter(prefix="/api", tags=["steps"])
logger = logging.getLogger(__name__)

step_service = StepService()

# Valid step IDs for validation
VALID_STEP_IDS = {"register", "voting", "documents", "polling", "results"}


@router.get(
    "/steps",
    response_model=StepsResponse,
    responses={500: {"model": ErrorResponse}},
    summary="Get All Step Guides",
    description="Returns all available step-by-step election guides."
)
async def get_all_steps() -> JSONResponse:
    """Get all available step-by-step guides"""
    try:
        steps = step_service.get_all_steps()

        return JSONResponse(content={
            "success": True,
            "count": len(steps),
            "data": [step.model_dump() for step in steps]
        })

    except Exception as e:
        logger.error(f"[STEPS ERROR] {e}", exc_info=True)
        raise HTTPException(500, detail="Failed to fetch step guides.")


@router.get(
    "/steps/{step_id}",
    response_model=StepDetailResponse,
    responses={
        404: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    },
    summary="Get Specific Step Guide",
    description=(
        "Get a specific step-by-step guide. "
        "Available: `register`, `voting`, `documents`, `polling`, `results`"
    )
)
async def get_step(step_id: str) -> JSONResponse:
    """
    Get specific step-by-step guide (India election flow).

    Available step_ids:
    - **register** → Voter registration (Electoral Roll)
    - **voting** → How to vote using EVM
    - **documents** → Required ID proofs
    - **polling** → Polling booth process
    - **results** → Counting & results
    """
    try:
        # ✅ Validate step_id FIRST (avoid building unnecessary objects)
        if step_id not in VALID_STEP_IDS:
            raise HTTPException(
                status_code=404,
                detail=f"Step '{step_id}' not found. Available: {sorted(VALID_STEP_IDS)}"
            )

        # ✅ Only build the requested step (optimized — no wasted computation)
        step_builders = {
            "register": step_service.get_registration_steps,
            "voting": step_service.get_voting_steps,
            "documents": step_service.get_document_steps,
            "polling": step_service.get_polling_steps,
            "results": step_service.get_results_steps,
        }

        step_data = step_builders[step_id]()

        return JSONResponse(content={
            "success": True,
            "step_id": step_id,
            "data": step_data.model_dump(),
            "next_options": [
                "Explain more",
                "Show timeline",
                "Start quiz",
                "Go to next step"
            ]
        })

    except HTTPException:
        raise

    except Exception as e:
        logger.error(f"[STEP ERROR] {e}", exc_info=True)
        raise HTTPException(500, detail="Failed to fetch step guide.")