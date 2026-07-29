import requests

from app.core.config import settings


class ReportGeneratorError(Exception):
    """Base error raised by the Ollama report generator."""


class ReportGeneratorTimeoutError(ReportGeneratorError):
    """Ollama did not respond within the configured timeout."""


class ReportGeneratorUnavailableError(ReportGeneratorError):
    """Ollama could not be reached."""


class ReportGeneratorHTTPError(ReportGeneratorError):
    """Ollama returned an unsuccessful HTTP status."""


class ReportGeneratorResponseError(ReportGeneratorError):
    """Ollama returned an invalid response body."""


class Llama:
    def __init__(
        self,
        model_name: str = settings.llama_model,
        host: str = settings.llama_url,
        timeout: tuple[float, float] = (5.0, 180.0),
        readiness_timeout: tuple[float, float] = (2.0, 5.0),
    ) -> None:
        self.model_name = model_name
        self.url = f"{host.rstrip('/')}/api/generate"
        self.readiness_url = f"{host.rstrip('/')}/api/tags"
        self.timeout = timeout
        self.readiness_timeout = readiness_timeout

    def check_readiness(self) -> None:
        try:
            response = requests.get(
                self.readiness_url,
                timeout=self.readiness_timeout,
            )
        except requests.Timeout as exc:
            raise ReportGeneratorTimeoutError(
                "Ollama readiness check timed out"
            ) from exc
        except requests.ConnectionError as exc:
            raise ReportGeneratorUnavailableError(
                "Could not connect to Ollama"
            ) from exc
        except requests.RequestException as exc:
            raise ReportGeneratorError(
                "Ollama readiness check failed"
            ) from exc

        try:
            response.raise_for_status()
        except requests.HTTPError as exc:
            raise ReportGeneratorHTTPError(
                f"Ollama readiness check returned HTTP {response.status_code}"
            ) from exc

    def generate(self, prompt: str) -> str:
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "temperature": 0.4,
            "top_p": 0.9,
            "top_k": 40,
            "repeat_penalty": 1.2,
            "num_predict": 1200,
            "stream": False,
        }

        try:
            response = requests.post(
                self.url,
                json=payload,
                timeout=self.timeout,
            )
        except requests.Timeout as exc:
            raise ReportGeneratorTimeoutError(
                "Ollama request timed out"
            ) from exc
        except requests.ConnectionError as exc:
            raise ReportGeneratorUnavailableError(
                "Could not connect to Ollama"
            ) from exc
        except requests.RequestException as exc:
            raise ReportGeneratorError("Ollama request failed") from exc

        try:
            response.raise_for_status()
        except requests.HTTPError as exc:
            raise ReportGeneratorHTTPError(
                f"Ollama returned HTTP {response.status_code}"
            ) from exc

        try:
            data = response.json()
        except ValueError as exc:
            raise ReportGeneratorResponseError(
                "Ollama returned invalid JSON"
            ) from exc

        report = data.get("response") if isinstance(data, dict) else None
        if not isinstance(report, str):
            raise ReportGeneratorResponseError(
                "Ollama response does not contain report text"
            )

        return report
