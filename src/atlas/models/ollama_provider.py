"""Local Ollama model provider for Project ATLAS."""

from ollama import Client, ResponseError

from atlas.models.base import (
    ModelConfigurationError,
    ModelError,
    ModelProvider,
)


class OllamaModelProvider(ModelProvider):
    """Generate responses using a locally running Ollama model."""

    def __init__(
        self,
        model: str,
        host: str = "http://localhost:11434",
    ) -> None:
        """Initialize the Ollama provider."""

        cleaned_model = model.strip()
        cleaned_host = host.strip()

        if not cleaned_model:
            raise ModelConfigurationError("An Ollama model name is required.")

        if not cleaned_host:
            raise ModelConfigurationError("An Ollama host address is required.")

        self._model = cleaned_model
        self._client = Client(host=cleaned_host)

    @property
    def provider_name(self) -> str:
        """Return the provider name."""
        return "Ollama"

    def generate_response(self, user_message: str) -> str:
        """Generate a response using the configured Ollama model."""

        cleaned_message = user_message.strip()

        if not cleaned_message:
            return "I did not receive a message."

        try:
            response = self._client.chat(
                model=self._model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are ATLAS, a professional personal engineering "
                            "assistant. Be helpful, accurate, concise, and "
                            "transparent about uncertainty."
                        ),
                    },
                    {
                        "role": "user",
                        "content": cleaned_message,
                    },
                ],
                stream=False,
            )

        except ResponseError as error:
            raise ModelError(f"Ollama rejected the request: {error.error}") from error

        except ConnectionError as error:
            raise ModelError(
                "Could not connect to Ollama. Make sure the Ollama application is running."
            ) from error

        except Exception as error:
            raise ModelError(f"Ollama request failed: {error}") from error

        content = response.message.content

        if content is None:
            raise ModelError("Ollama returned an empty response.")

        output_text = content.strip()

        if not output_text:
            raise ModelError("Ollama returned an empty response.")

        return output_text
