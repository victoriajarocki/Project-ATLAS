"""Shared interfaces and exceptions for ATLAS model providers."""

from abc import ABC, abstractmethod


class ModelError(RuntimeError):
    """Base exception raised when a model provider fails."""


class ModelConfigurationError(ModelError):
    """Raised when a model provider is configured incorrectly."""


class ModelProvider(ABC):
    """Abstract interface implemented by every ATLAS model provider."""

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Return the provider's human-readable name."""

    @abstractmethod
    def generate_response(self, user_message: str) -> str:
        """Generate a response to a user message."""
