"""Deterministic model provider used for local development and tests."""

from atlas.models.base import ModelProvider


class MockModelProvider(ModelProvider):
    """Return predictable responses without contacting an external model."""

    @property
    def provider_name(self) -> str:
        """Return the provider name."""
        return "Mock"

    def generate_response(self, user_message: str) -> str:
        """Return a deterministic response for development."""
        cleaned_message = user_message.strip()

        if not cleaned_message:
            return "I did not receive a message."

        return f"Mock response to: {cleaned_message}"
