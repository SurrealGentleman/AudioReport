import asyncio
from io import BytesIO
from pathlib import Path

import pytest
from fastapi import UploadFile
from starlette.datastructures import Headers

from app.api import upload as upload_module
from app.api.upload import (
    AudioFileTooLargeError,
    EmptyAudioFileError,
    UnsupportedAudioFormatError,
    save_upload_to_temp,
)


def create_upload(
    content: bytes,
    filename: str | None = "meeting.wav",
    content_type: str = "audio/wav",
) -> UploadFile:
    return UploadFile(
        file=BytesIO(content),
        filename=filename,
        headers=Headers({"content-type": content_type}),
    )


def test_save_upload_to_temp_preserves_content_and_suffix() -> None:
    content = b"fake audio content"
    upload = create_upload(content)

    path = asyncio.run(save_upload_to_temp(upload))

    try:
        assert path.suffix == ".wav"
        assert path.read_bytes() == content
    finally:
        path.unlink(missing_ok=True)
        asyncio.run(upload.close())


def test_save_upload_to_temp_rejects_missing_filename() -> None:
    upload = create_upload(b"audio", filename=None)

    with pytest.raises(UnsupportedAudioFormatError):
        asyncio.run(save_upload_to_temp(upload))

    asyncio.run(upload.close())


@pytest.mark.parametrize(
    ("filename", "content_type"),
    [
        ("meeting.txt", "text/plain"),
        ("meeting.wav", "application/octet-stream"),
        ("meeting.mp3", "audio/wav"),
    ],
)
def test_save_upload_to_temp_rejects_unsupported_format(
    filename: str,
    content_type: str,
) -> None:
    upload = create_upload(
        b"audio",
        filename=filename,
        content_type=content_type,
    )

    with pytest.raises(UnsupportedAudioFormatError):
        asyncio.run(save_upload_to_temp(upload))

    asyncio.run(upload.close())


def test_save_upload_to_temp_rejects_empty_file() -> None:
    upload = create_upload(b"")

    with pytest.raises(EmptyAudioFileError):
        asyncio.run(save_upload_to_temp(upload))

    asyncio.run(upload.close())


def test_save_upload_to_temp_rejects_oversized_file() -> None:
    upload = create_upload(b"12345")

    with pytest.raises(AudioFileTooLargeError):
        asyncio.run(save_upload_to_temp(upload, max_size_bytes=4))

    asyncio.run(upload.close())


def test_save_upload_to_temp_removes_partial_file_on_read_error(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    controlled_path = tmp_path / "partial.wav"

    def create_controlled_temp_file(*, suffix: str, delete: bool):
        assert suffix == ".wav"
        assert delete is False
        return controlled_path.open("w+b")

    class BrokenUpload:
        filename = "meeting.wav"
        content_type = "audio/wav"

        def __init__(self) -> None:
            self.calls = 0

        async def read(self, _: int) -> bytes:
            self.calls += 1
            if self.calls == 1:
                return b"partial data"
            raise OSError("upload interrupted")

    monkeypatch.setattr(
        upload_module,
        "NamedTemporaryFile",
        create_controlled_temp_file,
    )

    with pytest.raises(OSError, match="upload interrupted"):
        asyncio.run(save_upload_to_temp(BrokenUpload()))  # type: ignore[arg-type]

    assert not controlled_path.exists()
