from functools import lru_cache
from typing import Annotated

from fastapi import Header, HTTPException, status

from app.core.config import settings
from app.services.report_generator import Llama
from app.services.report_service import ReportService
from app.services.transcriber import Whisper


def verify_api_key(
    x_api_key: Annotated[str | None, Header()] = None,
) -> None:
    if x_api_key != settings.api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key",
        )


@lru_cache
def get_transcriber() -> Whisper:
    return Whisper(
        model_name=settings.whisper_model,
        device=settings.device_for_ai,
    )


@lru_cache
def get_report_generator() -> Llama:
    return Llama()


@lru_cache
def get_report_service() -> ReportService:
    return ReportService(
        transcriber=get_transcriber(),
        generator=get_report_generator(),
    )