"""
FastAPI Application Factory — VoteIQ (Backend API Only)
Election Process Education Assistant

Includes:
- CORS with configurable origins
- Rate limiting middleware
- Security headers
- OpenAPI documentation with tags
"""

import time
import logging
from collections import defaultdict
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .config import config
from .routes.chat import router as chat_router
from .routes.timeline import router as timeline_router
from .routes.steps import router as steps_router

logger = logging.getLogger(__name__)

# -----------------------------
# 📊 OPENAPI TAG DESCRIPTIONS
# -----------------------------
TAGS_METADATA = [
    {
        "name": "chat",
        "description": "Conversational AI assistant for election education. Supports guide, timeline, and quiz modes."
    },
    {
        "name": "timeline",
        "description": "Election timeline data including phases, events, deadlines, and upcoming dates."
    },
    {
        "name": "steps",
        "description": "Step-by-step guides for voter registration, voting process, documents, polling, and results."
    },
    {
        "name": "system",
        "description": "Health checks, app info, and system status endpoints."
    }
]


# -----------------------------
# 🛡️ RATE LIMITER (In-Memory)
# -----------------------------
class RateLimiter:
    """Simple in-memory sliding window rate limiter"""

    def __init__(self, max_requests: int = 30, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._requests: dict = defaultdict(list)

    def is_allowed(self, client_ip: str) -> bool:
        """Check if client is within rate limit"""
        now = time.time()
        window_start = now - self.window_seconds

        # Clean old entries
        self._requests[client_ip] = [
            t for t in self._requests[client_ip] if t > window_start
        ]

        if len(self._requests[client_ip]) >= self.max_requests:
            return False

        self._requests[client_ip].append(now)
        return True

    def get_remaining(self, client_ip: str) -> int:
        """Get remaining requests for client"""
        now = time.time()
        window_start = now - self.window_seconds
        active = [t for t in self._requests[client_ip] if t > window_start]
        return max(0, self.max_requests - len(active))


def create_app() -> FastAPI:
    """Create and configure FastAPI application with security middleware"""

    app = FastAPI(
        title="VoteIQ — Election Process Education Assistant 🇮🇳",
        version="2.0.0",
        description=(
            "AI-powered API for understanding elections, voting, and timelines in India. "
            "Built with FastAPI and Google Gemini for the PromptWars Challenge."
        ),
        openapi_tags=TAGS_METADATA,
        docs_url="/docs",
        redoc_url="/redoc"
    )

    # Rate limiter instance
    rate_limiter = RateLimiter(
        max_requests=config.RATE_LIMIT_REQUESTS,
        window_seconds=config.RATE_LIMIT_WINDOW
    )

    # -----------------------------
    # 🌐 CORS CONFIG
    # -----------------------------
    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.ALLOWED_ORIGINS,
        allow_credentials=False,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["Content-Type", "Authorization", "X-Request-ID"],
    )

    # -----------------------------
    # 🛡️ SECURITY HEADERS MIDDLEWARE
    # -----------------------------
    @app.middleware("http")
    async def add_security_headers(request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Cache-Control"] = "no-store"
        return response

    # -----------------------------
    # ⏱️ RATE LIMITING MIDDLEWARE
    # -----------------------------
    @app.middleware("http")
    async def rate_limit_middleware(request: Request, call_next):
        # Skip rate limiting for docs and health
        if request.url.path in ("/docs", "/redoc", "/openapi.json", "/health"):
            return await call_next(request)

        client_ip = request.client.host if request.client else "unknown"

        if not rate_limiter.is_allowed(client_ip):
            logger.warning(f"Rate limit exceeded for {client_ip}")
            return JSONResponse(
                status_code=429,
                content={
                    "success": False,
                    "error": "rate_limit_exceeded",
                    "message": "Too many requests. Please wait and try again."
                }
            )

        response = await call_next(request)
        response.headers["X-RateLimit-Remaining"] = str(
            rate_limiter.get_remaining(client_ip)
        )
        response.headers["X-RateLimit-Limit"] = str(rate_limiter.max_requests)
        return response

    # -----------------------------
    # 📡 API ROUTES
    # -----------------------------
    app.include_router(chat_router)
    app.include_router(timeline_router)
    app.include_router(steps_router)

    # -----------------------------
    # 🏠 ROOT (API Info)
    # -----------------------------
    @app.get("/", tags=["system"], summary="API Root", description="Returns API info and available endpoints")
    async def root() -> dict:
        return {
            "name": "VoteIQ",
            "tagline": "Election Process Education Assistant",
            "version": "2.0.0",
            "docs": "/docs",
            "endpoints": {
                "chat": "POST /api/chat",
                "timeline": "GET /api/timeline",
                "steps": "GET /api/steps",
                "health": "GET /health"
            }
        }

    # -----------------------------
    # ❤️ HEALTH CHECK
    # -----------------------------
    @app.get("/health", tags=["system"], summary="Health Check", description="Returns API health status")
    async def health_check() -> dict:
        return {
            "status": "ok",
            "app": "VoteIQ",
            "version": "2.0.0",
            "mode": config.DEFAULT_MODE,
            "ai_enabled": config.ENABLE_AI
        }

    # -----------------------------
    # 📊 APP INFO
    # -----------------------------
    @app.get("/info", tags=["system"], summary="App Info", description="Returns application configuration details")
    async def app_info() -> dict:
        return {
            "name": "VoteIQ",
            "description": "Election Process Education Assistant",
            "country": config.ELECTION_COUNTRY,
            "default_mode": config.DEFAULT_MODE,
            "supported_modes": config.SUPPORTED_MODES,
            "environment": config.ENV
        }

    return app


# Uvicorn entry point
app = create_app()