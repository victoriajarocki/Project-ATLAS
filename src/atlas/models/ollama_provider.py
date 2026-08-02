"""Local Ollama model provider for Project ATLAS."""

from typing import Any

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

    def generate_response(
        self,
        user_message: str,
    ) -> str:
        """Generate a normal natural-language response."""
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
                            "/no_think\n"
                            "You are ATLAS, a professional personal "
                            "engineering assistant. Respond with only "
                            "the final answer. Never include internal "
                            "reasoning, analysis, planning, or <think> "
                            "tags. Be helpful, accurate, concise, and "
                            "transparent about uncertainty."
                        ),
                    },
                    {
                        "role": "user",
                        "content": (f"/no_think\n{cleaned_message}"),
                    },
                ],
                stream=False,
                think=False,
                keep_alive="10m",
                options={
                    "temperature": 0,
                    "num_predict": 256,
                },
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

        return self._clean_model_output(content)

    def generate_structured_response(
        self,
        user_message: str,
        schema: dict[str, Any],
    ) -> str:
        """Generate a response constrained by a JSON schema."""
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
                            "/no_think\n"
                            "You are ATLAS, a professional personal "
                            "engineering assistant. Follow the supplied "
                            "JSON schema exactly. Return only the JSON "
                            "object. Never include internal reasoning, "
                            "analysis, Markdown fences, or <think> tags."
                        ),
                    },
                    {
                        "role": "user",
                        "content": (f"/no_think\n{cleaned_message}"),
                    },
                ],
                format=schema,
                stream=False,
                think=False,
                keep_alive="10m",
                options={
                    "temperature": 0,
                    "num_predict": 512,
                },
            )

        except ResponseError as error:
            raise ModelError(f"Ollama rejected the structured request: {error.error}") from error

        except ConnectionError as error:
            raise ModelError(
                "Could not connect to Ollama. Make sure the Ollama application is running."
            ) from error

        except Exception as error:
            raise ModelError(f"Ollama structured request failed: {error}") from error

        content = response.message.content

        if content is None:
            raise ModelError("Ollama returned an empty structured response.")

        return self._clean_model_output(content)

    @staticmethod
    def _clean_model_output(
        content: str,
    ) -> str:
        """Remove leaked reasoning blocks from model output."""
        cleaned_content = content.strip()

        if "</think>" in cleaned_content:
            cleaned_content = cleaned_content.rsplit(
                "</think>",
                maxsplit=1,
            )[1].strip()

        if cleaned_content.startswith("<think>"):
            raise ModelError("Ollama returned reasoning without a final answer.")

        if not cleaned_content:
            raise ModelError("Ollama returned an empty final response.")

        return cleaned_content
