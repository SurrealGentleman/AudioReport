import asyncio
import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import get_report_generator
from app.schemas.health import HealthResponse
from app.services.report_generator import Llama, ReportGeneratorError

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    return HealthResponse(status="ok")


@router.get("/health/live", response_model=HealthResponse)
def liveness_check() -> HealthResponse:
    return HealthResponse(status="alive")


@router.get("/health/ready", response_model=HealthResponse)
async def readiness_check(
    generator: Annotated[Llama, Depends(get_report_generator)],
) -> HealthResponse:
    try:
        await asyncio.to_thread(generator.check_readiness)
    except ReportGeneratorError as exc:
        logger.warning("Readiness check failed: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service is not ready",
        ) from exc

    return HealthResponse(status="ready")
