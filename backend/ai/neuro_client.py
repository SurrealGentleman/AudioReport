import logging
from collections.abc import Sequence

import requests
from django.conf import settings

logger = logging.getLogger(__name__)


class AIServiceError(Exception):
    """The external AI service could not complete the request."""


class AIServiceTimeoutError(AIServiceError):
    """The external AI service exceeded the configured timeout."""


class AIInvalidResponseError(AIServiceError):
    """The external AI service returned an invalid response."""


class NeuroServerClient:
    def __init__(self, session=None):
        self.api_url = settings.AI_API_URL
        self.api_key = settings.AI_API_KEY
        self.timeout = (
            settings.AI_CONNECT_TIMEOUT,
            settings.AI_READ_TIMEOUT,
        )
        self.session = session or requests.Session()

    def generate_report(
        self,
        audio_file,
        participants: Sequence[str],
        meeting_date: str,
    ) -> dict:
        files = {
            "audio": (
                audio_file.name,
                audio_file.file,
                audio_file.content_type or "application/octet-stream",
            )
        }
        data = {
            "meeting_date": meeting_date,
            "participants": ", ".join(participants),
        }
        headers = {"x-api-key": self.api_key}

        try:
            response = self.session.post(
                self.api_url,
                files=files,
                data=data,
                headers=headers,
                timeout=self.timeout,
            )
            response.raise_for_status()
        except requests.Timeout as error:
            logger.warning("AI service request timed out.")
            raise AIServiceTimeoutError from error
        except requests.RequestException as error:
            logger.warning(
                "AI service request failed: %s",
                type(error).__name__,
            )
            raise AIServiceError from error

        try:
            payload = response.json()
        except ValueError as error:
            raise AIInvalidResponseError(
                "AI service response is not valid JSON."
            ) from error

        if not isinstance(payload, dict):
            raise AIInvalidResponseError("AI service response must be a JSON object.")
        return payload
