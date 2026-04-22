"""
Timeline endpoints for VoteIQ — Election Process Education Assistant
Provides election timeline, upcoming events, deadlines, and event search
"""

import logging
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from ..models import TimelineResponse, ErrorResponse
from ..services.timeline_service import TimelineService

router = APIRouter(prefix="/api", tags=["timeline"])
logger = logging.getLogger(__name__)

timeline_service = TimelineService()


@router.get(
    "/timeline",
    response_model=TimelineResponse,
    responses={500: {"model": ErrorResponse}},
    summary="Get Full Election Timeline",
    description="Returns the complete Indian election process timeline with all phases."
)
async def get_full_timeline() -> JSONResponse:
    """Get the complete election timeline (India-focused phases)"""
    try:
        timeline = timeline_service.get_full_timeline()

        return JSONResponse(content={
            "success": True,
            "count": len(timeline),
            "data": timeline
        })

    except Exception as e:
        logger.error(f"[TIMELINE ERROR] {e}", exc_info=True)
        raise HTTPException(500, detail="Failed to fetch timeline. Please try again.")


@router.get(
    "/timeline/upcoming",
    response_model=TimelineResponse,
    responses={500: {"model": ErrorResponse}},
    summary="Get Upcoming Events",
    description="Returns the next few relevant election events."
)
async def get_upcoming_events() -> JSONResponse:
    """Get upcoming election events (next few relevant phases)"""
    try:
        upcoming = timeline_service.get_upcoming_events()

        return JSONResponse(content={
            "success": True,
            "count": len(upcoming),
            "data": upcoming
        })

    except Exception as e:
        logger.error(f"[UPCOMING ERROR] {e}", exc_info=True)
        raise HTTPException(500, detail="Failed to fetch upcoming events.")


@router.get(
    "/timeline/deadlines",
    responses={500: {"model": ErrorResponse}},
    summary="Get Election Deadlines",
    description="Returns key election-related deadlines in Indian context."
)
async def get_deadlines() -> JSONResponse:
    """Get key election-related deadlines (India context)"""
    try:
        deadlines = timeline_service.get_deadline_info()

        return JSONResponse(content={
            "success": True,
            "data": deadlines
        })

    except Exception as e:
        logger.error(f"[DEADLINES ERROR] {e}", exc_info=True)
        raise HTTPException(500, detail="Failed to fetch deadlines.")


@router.get(
    "/timeline/event/{event_name}",
    responses={
        404: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    },
    summary="Search Event by Name",
    description="Search for a specific election event by name (case-insensitive)."
)
async def search_event(event_name: str) -> JSONResponse:
    """Search for a specific election event by name"""
    try:
        event = timeline_service.get_event_by_name(event_name)

        if not event:
            raise HTTPException(404, detail=f"Event '{event_name}' not found")

        return JSONResponse(content={
            "success": True,
            "data": event
        })

    except HTTPException:
        raise

    except Exception as e:
        logger.error(f"[EVENT SEARCH ERROR] {e}", exc_info=True)
        raise HTTPException(500, detail="Failed to search event.")