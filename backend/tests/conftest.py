"""
Shared test fixtures for VoteIQ test suite
"""

import pytest
from app.server import create_app
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    """Create a test client for API endpoint testing"""
    app = create_app()
    return TestClient(app)


@pytest.fixture
def app():
    """Create a FastAPI app instance for testing"""
    return create_app()