"""Shared interfaces and exceptions for ATLAS model providers."""

from abc import ABC, abstractmethod
from typing import Any


class ModelError(RuntimeError):
    """Base exception raised by ATLAS model providers."""


class ModelConfigurationError(ModelError):
    """Raised when a model provider is configured incorrectly."""


class ModelProvider(ABC):
    """Abstract interface implemented by every model provider."""

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Return the provider name."""

    @abstractmethod
    def generate_response(
        self,
        user_message: str,
    ) -> str:
        """Generate a model response."""

    def generate_structured_response(
        self,
        user_message: str,
        schema: dict[str, Any],
    ) -> str:
        """Generate a response constrained by a JSON schema.

        Providers without native structured-output support fall back
        to their normal response method.
        """
        del schema
        return self.generate_response(user_message)
