"""
VoteIQ — Election Process Education Assistant (Backend Package)

A FastAPI-based AI assistant for Indian election education,
powered by Google Gemini and Google Cloud Platform.

Modules:
- config: Centralized configuration with Secret Manager integration
- constants: Application-wide constants and magic string elimination
- models: Pydantic v2 request/response schemas
- server: Application factory with security middleware
- routes/: API endpoint handlers
- services/: Business logic and Google Cloud integrations
- utils/: Input validation and sanitization
"""

__version__ = "2.1.0"
__author__ = "VoteIQ Team"