"""
Abstract base service pattern for VoteIQ

Provides a consistent interface for all services with:
- Standardized initialization and health checking
- Common logging setup
- Type-safe service contracts
"""

import logging
from abc import ABC, abstractmethod
from typing import TypeVar, Generic

T = TypeVar("T")


class BaseService(ABC):
    """
    Abstract base class for all VoteIQ services.

    Enforces a consistent pattern across application and
    Google Cloud service implementations.
    """

    def __init__(self, service_name: str) -> None:
        self._service_name: str = service_name
        self._logger: logging.Logger = logging.getLogger(
            f"voteiq.services.{service_name}"
        )
        self._logger.debug(f"Service initialized: {service_name}")

    @property
    def service_name(self) -> str:
        """Return the service name for identification"""
        return self._service_name

    def log_info(self, message: str) -> None:
        """Log an info-level message with service context"""
        self._logger.info(f"[{self._service_name}] {message}")

    def log_error(self, message: str, exc: Exception = None) -> None:
        """Log an error with service context and optional exception"""
        self._logger.error(f"[{self._service_name}] {message}", exc_info=exc)

    def log_warning(self, message: str) -> None:
        """Log a warning with service context"""
        self._logger.warning(f"[{self._service_name}] {message}")


class CloudService(BaseService):
    """
    Base class for Google Cloud service integrations.

    Adds availability checking and graceful fallback pattern
    common to all GCP services (Firestore, Logging, Storage, etc.).
    """

    def __init__(self, service_name: str) -> None:
        super().__init__(service_name)
        self._available: bool = False

    @property
    def is_available(self) -> bool:
        """Check if the cloud service is connected and operational"""
        return self._available

    def _set_available(self, available: bool) -> None:
        """Update service availability status"""
        self._available = available
        status = "available" if available else "unavailable"
        self._logger.info(f"Cloud service {self._service_name}: {status}")
