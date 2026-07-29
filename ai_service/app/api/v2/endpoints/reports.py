import logging
from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError

from app.api.deps import get_report_service, verify_api_key
from app.api.upload import (
    AudioFileTooLargeError,
    EmptyAudioFileError,
    UnsupportedAudioFormatError,
    save_upload_to_temp,
)
from app.schemas.report import ReportRequest, ReportResponse
from app.services.report_service import ReportGenerationError, ReportService

router = APIRouter(prefix="/reports")
logger = logging.getLogger(__name__)


def parse_report_request(
    meeting_date: Annotated[date, Form()],
    participants: Annotated[str, Form(min_length=1, max_length=2000)],
) -> ReportRequest:
    try:
        return ReportRequest(
            meeting_date=meeting_date,
            participants=participants,
        )
    except ValidationError as exc:
        raise RequestValidationError(exc.errors()) from exc


@router.post("/generate", response_model=ReportResponse)
async def generate_report(
    audio: Annotated[UploadFile, File()],
    report_request: Annotated[ReportRequest, Depends(parse_report_request)],
    _: Annotated[None, Depends(verify_api_key)],
    report_service: Annotated[ReportService, Depends(get_report_service)],
) -> ReportResponse:
    temporary_path = None

    try:
        logger.info("Report generation started for file %r", audio.filename)
        temporary_path = await save_upload_to_temp(audio)
        report = await report_service.generate(
            audio_path=temporary_path,
            meeting_date=report_request.meeting_date.isoformat(),
            participants=report_request.participants,
        )
        logger.info("Report generation completed for file %r", audio.filename)
        return ReportResponse(report_text=report)
    except AudioFileTooLargeError as exc:
        logger.warning("Rejected oversized audio file %r", audio.filename)
        raise HTTPException(
            status_code=status.HTTP_413_CONTENT_TOO_LARGE,
            detail="Audio file is too large",
        ) from exc
    except UnsupportedAudioFormatError as exc:
        logger.warning("Rejected unsupported audio file %r", audio.filename)
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Unsupported audio format",
        ) from exc
    except EmptyAudioFileError as exc:
        logger.warning("Rejected empty audio file %r", audio.filename)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Audio file is empty",
        ) from exc
    except ReportGenerationError as exc:
        logger.exception("Report generation failed for file %r", audio.filename)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate report",
        ) from exc
    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)
        await audio.close()
