"""
Google Cloud Secret Manager integration for VoteIQ
Securely retrieves API keys and secrets from GCP Secret Manager
"""

import logging
import os
from typing import Optional
from functools import lru_cache

logger = logging.getLogger(__name__)


class SecretManagerService:
    """
    Google Cloud Secret Manager for secure credential management.

    Falls back to environment variables when Secret Manager is unavailable
    (local development or missing credentials).
    """

    def __init__(self):
        self._client = None
        self._project_id: Optional[str] = None
        self._available: bool = False
        self._init_client()

    def _init_client(self) -> None:
        """Initialize Secret Manager client"""
        try:
            from google.cloud import secretmanager

            self._client = secretmanager.SecretManagerServiceClient()
            self._project_id = os.getenv(
                "GOOGLE_CLOUD_PROJECT",
                os.getenv("GCP_PROJECT", "")
            )

            if self._project_id:
                self._available = True
                logger.info("🔐 Google Cloud Secret Manager initialized")
            else:
                logger.info("No GCP project set, using env vars for secrets")

        except ImportError:
            logger.info("google-cloud-secret-manager not installed, using env vars")
        except Exception as e:
            logger.warning(f"Secret Manager init failed ({e}), using env vars")

    @property
    def is_available(self) -> bool:
        """Check if Secret Manager is connected"""
        return self._available and self._client is not None

    @lru_cache(maxsize=16)
    def get_secret(self, secret_id: str, version: str = "latest") -> Optional[str]:
        """
        Retrieve a secret value from Google Cloud Secret Manager.
        Results are cached in memory to minimize API calls.

        Falls back to environment variable with same name if
        Secret Manager is unavailable.

        Args:
            secret_id: Secret name in Secret Manager
            version: Secret version (default: "latest")

        Returns:
            Secret value string, or None if not found
        """
        # Try Secret Manager first
        if self.is_available:
            try:
                name = f"projects/{self._project_id}/secrets/{secret_id}/versions/{version}"
                response = self._client.access_secret_version(request={"name": name})
                secret_value = response.payload.data.decode("UTF-8")
                logger.info(f"Secret '{secret_id}' retrieved from Secret Manager")
                return secret_value

            except Exception as e:
                logger.warning(f"Secret Manager access failed for '{secret_id}': {e}")

        # Fallback to environment variable
        env_value = os.getenv(secret_id)
        if env_value:
            logger.debug(f"Secret '{secret_id}' loaded from environment variable")
        return env_value

    def get_api_key(self) -> Optional[str]:
        """
        Retrieve the Google API key using priority:
        1. Secret Manager (production)
        2. GOOGLE_API_KEY env var (development)

        Returns:
            API key string or None
        """
        return self.get_secret("GOOGLE_API_KEY")

    def get_gemini_model(self) -> str:
        """
        Retrieve the Gemini model name.

        Returns:
            Model name string (defaults to gemini-1.5-pro)
        """
        return self.get_secret("GEMINI_MODEL") or "gemini-1.5-pro"
