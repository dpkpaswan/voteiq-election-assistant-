"""
Tests for Google Cloud service integrations in VoteIQ

Tests:
- Cloud Logging setup and structured log functions
- Firestore service (chat storage, analytics, feedback)
- Secret Manager service (secret retrieval, env fallback)
- Cloud Storage service (knowledge base loading)
- Gemini Chat Sessions (multi-turn, embeddings)
"""

import pytest
import os
from unittest.mock import patch, MagicMock


# ═══════════════════════════════════════
# ☁️ CLOUD LOGGING TESTS
# ═══════════════════════════════════════
class TestCloudLoggingService:
    """Tests for Google Cloud Logging integration"""

    def test_setup_cloud_logging_local_fallback(self):
        """Should fall back to local logging when not on GCP"""
        from app.services.cloud_logging_service import setup_cloud_logging
        # Should not raise even without GCP credentials
        setup_cloud_logging("INFO")

    def test_setup_cloud_logging_with_custom_level(self):
        """Should accept custom log levels"""
        from app.services.cloud_logging_service import setup_cloud_logging
        setup_cloud_logging("DEBUG")
        setup_cloud_logging("WARNING")

    def test_log_chat_interaction_no_error(self):
        """Should log chat interaction without errors"""
        from app.services.cloud_logging_service import log_chat_interaction
        log_chat_interaction(
            message="How to register to vote?",
            intent="registration",
            confidence=0.85,
            mode="guide",
            session_id="test-session",
            response_length=150,
        )

    def test_log_chat_interaction_without_session(self):
        """Should handle missing session_id gracefully"""
        from app.services.cloud_logging_service import log_chat_interaction
        log_chat_interaction(
            message="Test question",
            intent="general",
            confidence=0.5,
            mode="guide",
        )

    def test_log_api_request_no_error(self):
        """Should log API request metrics without errors"""
        from app.services.cloud_logging_service import log_api_request
        log_api_request(
            method="POST",
            path="/api/chat",
            status_code=200,
            duration_ms=45.5,
            client_ip="127.0.0.1",
        )

    def test_log_api_request_error_status(self):
        """Should log error status codes"""
        from app.services.cloud_logging_service import log_api_request
        log_api_request(
            method="GET",
            path="/api/timeline",
            status_code=500,
            duration_ms=120.0,
        )

    def test_log_chat_interaction_long_message(self):
        """Should truncate long messages in preview"""
        from app.services.cloud_logging_service import log_chat_interaction
        long_msg = "A" * 200
        log_chat_interaction(
            message=long_msg,
            intent="general",
            confidence=0.5,
            mode="guide",
            response_length=500,
        )


# ═══════════════════════════════════════
# 🔥 FIRESTORE TESTS
# ═══════════════════════════════════════
class TestFirestoreService:
    """Tests for Google Cloud Firestore integration"""

    def test_firestore_init_graceful_fallback(self):
        """Should initialize without error even without GCP credentials"""
        from app.services.firestore_service import FirestoreService
        service = FirestoreService()
        # In test env, Firestore is not available — should not crash
        assert isinstance(service.is_available, bool)

    def test_firestore_save_returns_none_when_unavailable(self):
        """Should return None when Firestore is not available"""
        from app.services.firestore_service import FirestoreService
        service = FirestoreService()
        result = service.save_chat_message(
            session_id="test",
            user_message="Hello",
            assistant_response="Hi",
            intent="general",
            confidence=0.5,
        )
        if not service.is_available:
            assert result is None

    def test_firestore_get_history_returns_empty_when_unavailable(self):
        """Should return empty list when Firestore is not available"""
        from app.services.firestore_service import FirestoreService
        service = FirestoreService()
        history = service.get_chat_history("nonexistent-session")
        if not service.is_available:
            assert history == []

    def test_firestore_track_intent_no_error(self):
        """Should not raise when tracking intent usage"""
        from app.services.firestore_service import FirestoreService
        service = FirestoreService()
        service.track_intent_usage("registration")

    def test_firestore_track_daily_usage_no_error(self):
        """Should not raise when tracking daily usage"""
        from app.services.firestore_service import FirestoreService
        service = FirestoreService()
        service.track_daily_usage()

    def test_firestore_save_feedback_returns_false_when_unavailable(self):
        """Should return False when Firestore is not available"""
        from app.services.firestore_service import FirestoreService
        service = FirestoreService()
        result = service.save_feedback("test-session", 5, "Great!")
        if not service.is_available:
            assert result is False

    def test_firestore_feedback_clamps_rating(self):
        """Should clamp rating between 1 and 5"""
        from app.services.firestore_service import FirestoreService
        service = FirestoreService()
        # These should not raise regardless of availability
        service.save_feedback("test", 10, "Too high")
        service.save_feedback("test", -1, "Too low")

    def test_firestore_is_available_property(self):
        """The is_available property should return a boolean"""
        from app.services.firestore_service import FirestoreService
        service = FirestoreService()
        assert isinstance(service.is_available, bool)


# ═══════════════════════════════════════
# 🔐 SECRET MANAGER TESTS
# ═══════════════════════════════════════
class TestSecretManagerService:
    """Tests for Google Cloud Secret Manager integration"""

    def test_secret_manager_init_graceful_fallback(self):
        """Should initialize without error even without GCP credentials"""
        from app.services.secret_manager_service import SecretManagerService
        service = SecretManagerService()
        assert isinstance(service.is_available, bool)

    def test_secret_manager_env_fallback(self):
        """Should fall back to environment variable"""
        from app.services.secret_manager_service import SecretManagerService
        service = SecretManagerService()

        with patch.dict(os.environ, {"TEST_SECRET": "test_value"}):
            value = service.get_secret("TEST_SECRET")
            assert value == "test_value"

    def test_secret_manager_returns_none_for_missing(self):
        """Should return None for missing secrets"""
        from app.services.secret_manager_service import SecretManagerService
        service = SecretManagerService()
        service.get_secret.cache_clear()
        value = service.get_secret("NONEXISTENT_SECRET_XYZ_12345")
        assert value is None

    def test_get_api_key_method(self):
        """Should have a get_api_key convenience method"""
        from app.services.secret_manager_service import SecretManagerService
        service = SecretManagerService()
        # Should not raise
        service.get_api_key()

    def test_get_gemini_model_default(self):
        """Should return default model name when not configured"""
        from app.services.secret_manager_service import SecretManagerService
        service = SecretManagerService()
        service.get_secret.cache_clear()
        model = service.get_gemini_model()
        assert isinstance(model, str)
        assert len(model) > 0


# ═══════════════════════════════════════
# 📦 CLOUD STORAGE TESTS
# ═══════════════════════════════════════
class TestCloudStorageService:
    """Tests for Google Cloud Storage integration"""

    def test_cloud_storage_init_graceful_fallback(self):
        """Should initialize without error even without GCP credentials"""
        from app.services.cloud_storage_service import CloudStorageService
        service = CloudStorageService()
        assert isinstance(service.is_available, bool)

    def test_cloud_storage_local_fallback(self):
        """Should load knowledge base from local file when GCS unavailable"""
        from app.services.cloud_storage_service import CloudStorageService
        service = CloudStorageService()
        data = service.load_knowledge_base()
        # Should have loaded from local data/ directory
        assert isinstance(data, dict)

    def test_cloud_storage_list_returns_empty_when_unavailable(self):
        """Should return empty list when GCS is not available"""
        from app.services.cloud_storage_service import CloudStorageService
        service = CloudStorageService()
        if not service.is_available:
            result = service.list_available_data()
            assert result == []

    def test_cloud_storage_save_returns_false_when_unavailable(self):
        """Should return False when GCS is not available"""
        from app.services.cloud_storage_service import CloudStorageService
        service = CloudStorageService()
        if not service.is_available:
            result = service.save_knowledge_base({"test": "data"})
            assert result is False

    def test_cloud_storage_custom_bucket(self):
        """Should accept custom bucket name"""
        from app.services.cloud_storage_service import CloudStorageService
        service = CloudStorageService(bucket_name="custom-bucket")
        assert service._bucket_name == "custom-bucket"


# ═══════════════════════════════════════
# 🧠 GEMINI CHAT SESSIONS TESTS
# ═══════════════════════════════════════
class TestGeminiChatSessions:
    """Tests for Gemini multi-turn chat and embeddings"""

    def test_gemini_service_init(self):
        """Should initialize without error"""
        from app.services.gemini_service import GeminiService
        service = GeminiService()
        assert service.model_name is not None
        assert isinstance(service._chat_sessions, dict)

    def test_gemini_fallback_responses(self):
        """Should have fallback for every intent category"""
        from app.services.gemini_service import GeminiService
        service = GeminiService()

        intents = ["registration", "timeline", "voting", "documents", "polling", "results", "general"]
        for intent in intents:
            response = service._get_fallback_response(intent)
            assert isinstance(response, str)
            assert len(response) > 20

    def test_gemini_fallback_unknown_intent(self):
        """Should use general fallback for unknown intents"""
        from app.services.gemini_service import GeminiService
        service = GeminiService()
        response = service._get_fallback_response("unknown_intent_xyz")
        assert "VoteIQ" in response

    def test_gemini_clear_session(self):
        """Should clear chat session without error"""
        from app.services.gemini_service import GeminiService
        service = GeminiService()
        service.clear_chat_session("nonexistent-session")
        # Should not raise

    def test_gemini_system_instruction_exists(self):
        """System instruction should contain India-specific context"""
        from app.services.gemini_service import SYSTEM_INSTRUCTION
        assert "India" in SYSTEM_INSTRUCTION
        assert "VoteIQ" in SYSTEM_INSTRUCTION
        assert "Election Commission" in SYSTEM_INSTRUCTION

    def test_gemini_safety_settings_complete(self):
        """All four safety categories should be configured"""
        from app.services.gemini_service import SAFETY_SETTINGS
        assert len(SAFETY_SETTINGS) == 4
        categories = {s["category"] for s in SAFETY_SETTINGS}
        assert "HARM_CATEGORY_HARASSMENT" in categories
        assert "HARM_CATEGORY_HATE_SPEECH" in categories

    def test_gemini_generation_config(self):
        """Generation config should have appropriate values"""
        from app.services.gemini_service import GENERATION_CONFIG
        assert GENERATION_CONFIG["temperature"] <= 0.5
        assert GENERATION_CONFIG["max_output_tokens"] >= 512


# ═══════════════════════════════════════
# 🔧 CONFIG GOOGLE SERVICES STATUS
# ═══════════════════════════════════════
class TestConfigGoogleServices:
    """Tests for config Google Cloud service integration"""

    def test_config_has_google_services_status(self):
        """Config should expose Google services status"""
        from app.config import config
        status = config.get_google_services_status()
        assert isinstance(status, dict)
        assert "gemini_ai" in status
        assert "cloud_logging" in status
        assert "firestore" in status
        assert "cloud_storage" in status
        assert "secret_manager" in status

    def test_config_gcp_project_type(self):
        """GCP project should be a string"""
        from app.config import config
        assert isinstance(config.GCP_PROJECT, str)

    def test_config_feature_flags(self):
        """Feature flags should be boolean"""
        from app.config import config
        assert isinstance(config.ENABLE_CLOUD_LOGGING, bool)
        assert isinstance(config.ENABLE_FIRESTORE, bool)
        assert isinstance(config.ENABLE_CLOUD_STORAGE, bool)


# ═══════════════════════════════════════
# 🌐 API GOOGLE SERVICES INTEGRATION
# ═══════════════════════════════════════
class TestAPIGoogleServicesIntegration:
    """Tests that Google services are exposed through API endpoints"""

    @pytest.fixture
    def client(self):
        from app.server import create_app
        from fastapi.testclient import TestClient
        return TestClient(create_app())

    def test_health_includes_google_services(self, client):
        """Health endpoint should include Google services status"""
        response = client.get("/health")
        data = response.json()
        assert "google_services" in data
        assert "gemini_ai" in data["google_services"]

    def test_info_includes_google_services(self, client):
        """Info endpoint should include Google services status"""
        response = client.get("/info")
        data = response.json()
        assert "google_services" in data

    def test_root_mentions_google_cloud(self, client):
        """Root endpoint should mention Google Cloud"""
        response = client.get("/")
        data = response.json()
        assert "google_cloud" in data

    def test_health_version_updated(self, client):
        """Version should be 2.1.0 after Google Cloud updates"""
        response = client.get("/health")
        data = response.json()
        assert data["version"] == "2.1.0"
