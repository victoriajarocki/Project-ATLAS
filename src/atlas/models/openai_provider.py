"""OpenAI model provider for Project ATLAS."""

from openai import OpenAI

from atlas.models.base import ModelConfigurationError, ModelError, ModelProvider


class OpenAIModelProvider(ModelProvider):
    """Generate ATLAS responses using the OpenAI Responses API."""

    def __init__(self, api_key: str | None, model: str) -> None:
        """Initialize the provider with an API key and model name."""
        if not api_key:
            raise ModelConfigurationError("OPENAI_API_KEY is required when ATLAS_PROVIDER=openai.")

        if not model.strip():
            raise ModelConfigurationError("An OpenAI model name is required.")

        self._model = model
        self._client = OpenAI(api_key=api_key)

    @property
    def provider_name(self) -> str:
        """Return the provider name."""
        return "OpenAI"

    def generate_response(self, user_message: str) -> str:
        """Generate a response using the OpenAI Responses API."""
        cleaned_message = user_message.strip()

        if not cleaned_message:
            return "I did not receive a message."

        try:
            response = self._client.responses.create(
                model=self._model,
                instructions=(
                    "You are ATLAS, a professional personal engineering assistant. "
                    "Be helpful, accurate, concise, and transparent about uncertainty."
                ),
                input=cleaned_message,
            )
        except Exception as error:
            raise ModelError(f"OpenAI request failed: {error}") from error

        output_text = response.output_text.strip()

        if not output_text:
            raise ModelError("OpenAI returned an empty response.")

        return output_text
