"""
Tests for VoteIQ constants and base service patterns

Validates:
- All constants are properly typed and non-empty
- Intent, mode, and step ID sets are consistent
- BaseService and CloudService patterns work correctly
- Constants are used consistently across the codebase
"""

import pytest
from app.constants import (
    APP_NAME, APP_VERSION, APP_DESCRIPTION, APP_COUNTRY,
    API_PREFIX, DOCS_URL,
    VALID_INTENTS, VALID_MODES, VALID_STEP_IDS,
    INTENT_REGISTRATION, INTENT_GENERAL, INTENT_VOTING,
    MODE_GUIDE, MODE_TIMELINE, MODE_QUIZ,
    STEP_REGISTER, STEP_VOTING,
    MIN_INPUT_LENGTH, MAX_INPUT_LENGTH,
    DEFAULT_GEMINI_MODEL, LOW_CONFIDENCE_THRESHOLD,
    DEFAULT_SOURCES,
    ERROR_INVALID_INPUT, ERROR_INTERNAL,
    HTTP_OK, HTTP_BAD_REQUEST, HTTP_NOT_FOUND, HTTP_RATE_LIMITED,
)


# ═══════════════════════════════════════
# 📋 CONSTANTS TESTS
# ═══════════════════════════════════════
class TestAppConstants:
    """Tests for application-level constants"""

    def test_app_name_is_voteiq(self):
        assert APP_NAME == "VoteIQ"

    def test_app_version_format(self):
        parts = APP_VERSION.split(".")
        assert len(parts) == 3
        assert all(part.isdigit() for part in parts)

    def test_app_country_is_india(self):
        assert APP_COUNTRY == "India"

    def test_api_prefix(self):
        assert API_PREFIX == "/api"

    def test_docs_url(self):
        assert DOCS_URL == "/docs"


class TestIntentConstants:
    """Tests for intent classification constants"""

    def test_valid_intents_has_7_categories(self):
        assert len(VALID_INTENTS) == 7

    def test_registration_in_valid_intents(self):
        assert INTENT_REGISTRATION in VALID_INTENTS

    def test_general_in_valid_intents(self):
        assert INTENT_GENERAL in VALID_INTENTS

    def test_voting_in_valid_intents(self):
        assert INTENT_VOTING in VALID_INTENTS

    def test_valid_intents_is_frozenset(self):
        assert isinstance(VALID_INTENTS, frozenset)


class TestModeConstants:
    """Tests for assistant mode constants"""

    def test_valid_modes_has_3_modes(self):
        assert len(VALID_MODES) == 3

    def test_guide_mode_exists(self):
        assert MODE_GUIDE in VALID_MODES

    def test_timeline_mode_exists(self):
        assert MODE_TIMELINE in VALID_MODES

    def test_quiz_mode_exists(self):
        assert MODE_QUIZ in VALID_MODES


class TestStepConstants:
    """Tests for step guide constants"""

    def test_valid_step_ids_has_5_steps(self):
        assert len(VALID_STEP_IDS) == 5

    def test_register_step_exists(self):
        assert STEP_REGISTER in VALID_STEP_IDS

    def test_voting_step_exists(self):
        assert STEP_VOTING in VALID_STEP_IDS


class TestValidationConstants:
    """Tests for input validation constants"""

    def test_min_length_is_3(self):
        assert MIN_INPUT_LENGTH == 3

    def test_max_length_is_500(self):
        assert MAX_INPUT_LENGTH == 500

    def test_min_less_than_max(self):
        assert MIN_INPUT_LENGTH < MAX_INPUT_LENGTH


class TestAIConstants:
    """Tests for AI-related constants"""

    def test_default_model_is_gemini(self):
        assert "gemini" in DEFAULT_GEMINI_MODEL

    def test_confidence_threshold_valid(self):
        assert 0.0 < LOW_CONFIDENCE_THRESHOLD < 1.0


class TestSourceConstants:
    """Tests for source reference constants"""

    def test_default_sources_has_3(self):
        assert len(DEFAULT_SOURCES) == 3

    def test_eci_in_sources(self):
        assert any("eci.gov.in" in s for s in DEFAULT_SOURCES)


class TestErrorConstants:
    """Tests for error message constants"""

    def test_invalid_input_error_not_empty(self):
        assert len(ERROR_INVALID_INPUT) > 10

    def test_internal_error_not_empty(self):
        assert len(ERROR_INTERNAL) > 10


class TestHTTPConstants:
    """Tests for HTTP status code constants"""

    def test_http_ok(self):
        assert HTTP_OK == 200

    def test_http_bad_request(self):
        assert HTTP_BAD_REQUEST == 400

    def test_http_not_found(self):
        assert HTTP_NOT_FOUND == 404

    def test_http_rate_limited(self):
        assert HTTP_RATE_LIMITED == 429


# ═══════════════════════════════════════
# 🏗️ BASE SERVICE TESTS
# ═══════════════════════════════════════
class TestBaseService:
    """Tests for abstract base service pattern"""

    def test_base_service_init(self):
        from app.services.base import BaseService

        class ConcreteService(BaseService):
            pass

        service = ConcreteService("test_service")
        assert service.service_name == "test_service"

    def test_base_service_logging_methods(self):
        from app.services.base import BaseService

        class ConcreteService(BaseService):
            pass

        service = ConcreteService("test")
        # Should not raise
        service.log_info("test info")
        service.log_warning("test warning")
        service.log_error("test error")

    def test_cloud_service_availability(self):
        from app.services.base import CloudService

        class ConcreteCloud(CloudService):
            pass

        service = ConcreteCloud("test_cloud")
        assert service.is_available is False

        service._set_available(True)
        assert service.is_available is True
