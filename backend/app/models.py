"""
Pydantic models for request/response validation — VoteIQ
Includes OpenAPI examples for interactive documentation
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum


# -----------------------------
# 🧠 INTENT TYPES
# -----------------------------
class IntentType(str, Enum):
    """Supported user intent categories for election queries"""
    REGISTRATION = "registration"
    TIMELINE = "timeline"
    VOTING = "voting"
    DOCUMENTS = "documents"
    POLLING = "polling"
    RESULTS = "results"
    GENERAL = "general"


# -----------------------------
# 💬 CHAT MODELS
# -----------------------------
class ChatRequest(BaseModel):
    """User chat message to VoteIQ assistant"""
    message: str = Field(
        ...,
        min_length=3,
        max_length=500,
        description="User's election-related question",
        json_schema_extra={"examples": ["How do I register to vote in India?"]}
    )
    session_id: Optional[str] = Field(
        None,
        description="Session tracking ID for conversation continuity",
        json_schema_extra={"examples": ["sess_1713800000000"]}
    )
    mode: Optional[str] = Field(
        "guide",
        description="Assistant mode: guide, timeline, or quiz",
        json_schema_extra={"examples": ["guide"]}
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "message": "How do I register to vote in India?",
                    "session_id": "sess_1713800000000",
                    "mode": "guide"
                }
            ]
        }
    }


class ChatResponseData(BaseModel):
    """Structured assistant response data"""
    response: str = Field(..., description="Assistant's text response")
    intent: str = Field(..., description="Detected user intent category")
    confidence: Optional[float] = Field(None, description="Intent classification confidence (0.0-1.0)")
    mode: Optional[str] = Field(None, description="Current assistant mode")
    data: Optional[Any] = Field(None, description="Structured data (timeline events, step guides, etc.)")
    follow_up_suggestions: List[str] = Field(default_factory=list, description="Suggested follow-up questions")
    sources: List[str] = Field(default_factory=list, description="Reference sources")


class ChatResponse(BaseModel):
    """Full chat API response envelope"""
    success: bool = Field(True, description="Whether the request was successful")
    data: ChatResponseData = Field(..., description="Response payload")
    context: Dict[str, str] = Field(default_factory=dict, description="Request context")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "success": True,
                    "data": {
                        "response": "To vote in India, you must be registered in the Electoral Roll.",
                        "intent": "registration",
                        "confidence": 0.85,
                        "mode": "guide",
                        "data": None,
                        "follow_up_suggestions": [
                            "How do I check if I'm on the Electoral Roll?",
                            "Can I apply for a Voter ID online?"
                        ],
                        "sources": [
                            "Election Commission of India (eci.gov.in)",
                            "National Voters' Service Portal (nvsp.in)"
                        ]
                    },
                    "context": {"country": "India", "mode": "guide"}
                }
            ]
        }
    }


# -----------------------------
# 🗓️ TIMELINE MODELS
# -----------------------------
class TimelineEvent(BaseModel):
    """A single election timeline event"""
    event: str = Field(..., description="Event name")
    description: str = Field(..., description="Event description")
    date: Optional[str] = Field(None, description="Event date (ISO format if available)")
    phase: Optional[int] = Field(None, description="Election phase number")
    days_remaining: Optional[int] = Field(None, description="Days until event")


class TimelineResponse(BaseModel):
    """Timeline API response"""
    success: bool = True
    count: int = Field(..., description="Number of timeline events")
    data: List[Dict[str, Any]] = Field(..., description="Timeline events")


# -----------------------------
# 🪜 STEP-BY-STEP MODELS
# -----------------------------
class ElectionStep(BaseModel):
    """A step-by-step election guide"""
    step_id: str = Field(..., description="Unique step identifier")
    title: str = Field(..., description="Step title")
    description: str = Field(..., description="Step description")
    actions: List[str] = Field(..., description="Ordered list of actions to take")
    estimated_time: str = Field(..., description="Estimated time to complete")
    resources: List[str] = Field(..., description="Helpful resources and links")
    next_step: Optional[str] = Field(None, description="ID of the next step in sequence")


class StepsResponse(BaseModel):
    """Steps API response"""
    success: bool = True
    count: int = Field(..., description="Number of steps")
    data: List[Dict[str, Any]] = Field(..., description="Step guide data")


class StepDetailResponse(BaseModel):
    """Single step detail response"""
    success: bool = True
    step_id: str = Field(..., description="Step identifier")
    data: Dict[str, Any] = Field(..., description="Step details")
    next_options: List[str] = Field(..., description="Available next actions")


# -----------------------------
# 📊 GENERIC API RESPONSE
# -----------------------------
class APIResponse(BaseModel):
    """Generic API response wrapper"""
    success: bool = Field(True, description="Request success status")
    message: Optional[str] = Field(None, description="Human-readable message")
    data: Optional[Dict[str, Any]] = Field(None, description="Response data payload")


# -----------------------------
# ❌ ERROR RESPONSE
# -----------------------------
class ErrorResponse(BaseModel):
    """Standardized error response"""
    success: bool = Field(False, description="Always false for errors")
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="User-friendly error message")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "success": False,
                    "error": "validation_error",
                    "message": "Message must be between 3 and 500 characters"
                }
            ]
        }
    }