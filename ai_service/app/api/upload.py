from pathlib import Path
from tempfile import NamedTemporaryFile

from fastapi import UploadFile

from app.core.config import settings


CHUNK_SIZE = 1024 * 1024
ALLOWED_AUDIO_FORMATS: dict[str, frozenset[str]] = {
    ".flac": frozenset({"audio/flac", "audio/x-flac"}),
    ".m4a": frozenset({"audio/m4a", "audio/mp4", "audio/x-m4a"}),
    ".mp3": frozenset({"audio/mp3", "audio/mpeg"}),
    ".ogg": frozenset({"application/ogg", "audio/ogg"}),
    ".wav": frozenset({"audio/wav", "audio/wave", "audio/x-wav"}),
    ".webm": frozenset({"audio/webm", "video/webm"}),
}


class UploadValidationError(Exception):
    """Base error for invalid audio uploads."""


class UnsupportedAudioFormatError(UploadValidationError):
    """The filename extension or MIME type is not allowed."""


class AudioFileTooLargeError(UploadValidationError):
    """The uploaded audio exceeds the configured size limit."""


class EmptyAudioFileError(UploadValidationError):
    """The uploaded audio contains no data."""


def validate_audio_format(upload: UploadFile) -> str:
    suffix = Path(upload.filename or "").suffix.lower()
    content_type = (upload.content_type or "").split(";", maxsplit=1)[0].lower()
    allowed_content_types = ALLOWED_AUDIO_FORMATS.get(suffix)

    if allowed_content_types is None or content_type not in allowed_content_types:
        raise UnsupportedAudioFormatError(
            f"Unsupported audio format: {suffix or '<missing extension>'}"
        )

    return suffix


async def save_upload_to_temp(
    upload: UploadFile,
    max_size_bytes: int = settings.max_audio_file_size_mb * 1024 * 1024,
) -> Path:
    suffix = validate_audio_format(upload)
    path: Path | None = None
    total_size = 0

    try:
        with NamedTemporaryFile(suffix=suffix, delete=False) as file:
            path = Path(file.name)

            while chunk := await upload.read(CHUNK_SIZE):
                total_size += len(chunk)
                if total_size > max_size_bytes:
                    raise AudioFileTooLargeError(
                        f"Audio file exceeds {max_size_bytes} bytes"
                    )
                file.write(chunk)

        if total_size == 0:
            raise EmptyAudioFileError("Audio file is empty")
    except Exception:
        if path is not None:
            path.unlink(missing_ok=True)
        raise

    return path
