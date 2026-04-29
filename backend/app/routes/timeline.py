"""
Timeline endpoints for VoteIQ — Election Process Education Assistant

Provides:
- Full election timeline with all phases
- Upcoming election events (date-aware filtering)
- Key election deadlines (India-specific)
- Event search by name (case-insensitive)
"""

import logging
from typing import Dict, Any, List

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from ..constants import API_PREFIX, HTTP_NOT_FOUND, HTTP_INTERNAL_ERROR
from ..models import TimelineResponse, ErrorResponse
from ..services.timeline_service import TimelineService

router = APIRouter(prefix=API_PREFIX, tags=["timeline"])
logger = logging.getLogger(__name__)

# Singleton service instance
_timeline_service = TimelineService()


@router.get(
    "/timeline",
    response_model=TimelineResponse,
    responses={500: {"model": ErrorResponse}},
    summary="Get Full Election Timeline",
    description="Returns the complete Indian election process timeline with all phases.",
)
async def get_full_timeline() -> JSONResponse:
    """Get the complete election timeline (India — all phases from ECI)."""
    try:
        timeline: List[Dict[str, Any]] = _timeline_service.get_full_timeline()

        return JSONResponse(content={
            "success": True,
            "count": len(timeline),
            "data": timeline,
        })

    except Exception as e:
        logger.error(f"[TIMELINE ERROR] {e}", exc_info=True)
        raise HTTPException(
            status_code=HTTP_INTERNAL_ERROR,
            detail="Failed to fetch timeline. Please try again.",
        )


@router.get(
    "/timeline/upcoming",
    response_model=TimelineResponse,
    responses={500: {"model": ErrorResponse}},
    summary="Get Upcoming Events",
    description="Returns the next few relevant election events.",
)
async def get_upcoming_events() -> JSONResponse:
    """Get upcoming election events (next few relevant phases)."""
    try:
        upcoming: List[Dict[str, Any]] = _timeline_service.get_upcoming_events()

        return JSONResponse(content={
            "success": True,
            "count": len(upcoming),
            "data": upcoming,
        })

    except Exception as e:
        logger.error(f"[UPCOMING ERROR] {e}", exc_info=True)
        raise HTTPException(
            status_code=HTTP_INTERNAL_ERROR,
            detail="Failed to fetch upcoming events.",
        )


@router.get(
    "/timeline/deadlines",
    responses={500: {"model": ErrorResponse}},
    summary="Get Election Deadlines",
    description="Returns key election-related deadlines in Indian context.",
)
async def get_deadlines() -> JSONResponse:
    """Get key election-related deadlines (India-specific rules)."""
    try:
        deadlines: Dict[str, Any] = _timeline_service.get_deadline_info()

        return JSONResponse(content={
            "success": True,
            "data": deadlines,
        })

    except Exception as e:
        logger.error(f"[DEADLINES ERROR] {e}", exc_info=True)
        raise HTTPException(
            status_code=HTTP_INTERNAL_ERROR,
            detail="Failed to fetch deadlines.",
        )


@router.get(
    "/timeline/event/{event_name}",
    responses={
        404: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
    summary="Search Event by Name",
    description="Search for a specific election event by name (case-insensitive).",
)
async def search_event(event_name: str) -> JSONResponse:
    """Search for a specific election event by name (fuzzy, case-insensitive)."""
    try:
        event: Dict[str, Any] = _timeline_service.get_event_by_name(event_name)

        if not event:
            raise HTTPException(
                status_code=HTTP_NOT_FOUND,
                detail=f"Event '{event_name}' not found.",
            )

        return JSONResponse(content={
            "success": True,
            "data": event,
        })

    except HTTPException:
        raise

    except Exception as e:
        logger.error(f"[EVENT SEARCH ERROR] {e}", exc_info=True)
        raise HTTPException(
            status_code=HTTP_INTERNAL_ERROR,
            detail="Failed to search event.",
        )