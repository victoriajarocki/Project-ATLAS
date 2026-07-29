"""Core application coordinator for Project ATLAS."""

from atlas.models.base import ModelProvider


class AtlasApp:
    """Coordinate user requests with ATLAS subsystems."""

    def __init__(self, model_provider: ModelProvider) -> None:
        """Initialize ATLAS with a configured model provider."""
        self._model_provider = model_provider

    @property
    def provider_name(self) -> str:
        """Return the active model provider name."""
        return self._model_provider.provider_name

    def process_message(self, user_message: str) -> str:
        """Process one user message and return ATLAS's response."""
        cleaned_message = user_message.strip()

        if not cleaned_message:
            return "I did not receive a message."

        return self._model_provider.generate_response(cleaned_message)
