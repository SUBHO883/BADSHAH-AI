import requests

from backend.config import (
    OLLAMA_BASE_URL,
    OLLAMA_MODEL,
    OLLAMA_TIMEOUT,
)


class OllamaError(Exception):
    """Raised when Ollama communication fails."""


class OllamaClient:

    def __init__(self):
        self.base_url = OLLAMA_BASE_URL.rstrip("/")
        self.model = OLLAMA_MODEL

    def health(self) -> bool:
        try:
            response = requests.get(
                f"{self.base_url}/api/tags",
                timeout=10,
            )

            return response.ok

        except requests.RequestException:
            return False

    def models(self):
        try:
            response = requests.get(
                f"{self.base_url}/api/tags",
                timeout=10,
            )

            response.raise_for_status()

            data = response.json()

            return [
                item.get("name", "")
                for item in data.get("models", [])
            ]

        except (
            requests.RequestException,
            ValueError,
        ) as exc:
            raise OllamaError(
                f"Unable to read Ollama models: {exc}"
            ) from exc

    def generate(self, prompt: str) -> str:

        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
        }

        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=OLLAMA_TIMEOUT,
            )

            response.raise_for_status()

        except requests.RequestException as exc:
            raise OllamaError(
                f"Ollama connection failed: {exc}"
            ) from exc

        try:
            data = response.json()

        except ValueError as exc:
            raise OllamaError(
                "Ollama returned invalid JSON."
            ) from exc

        answer = data.get(
            "response",
            "",
        ).strip()

        if not answer:
            raise OllamaError(
                "Ollama returned an empty response."
            )

        return answer