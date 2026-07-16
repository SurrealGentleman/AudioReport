import asyncio
from pathlib import Path
from unittest.mock import Mock

import pytest

from app.services.report_service import ReportGenerationError, ReportService


def test_generate_transcribes_audio_and_generates_report(tmp_path: Path) -> None:
    audio_path = tmp_path / "meeting.wav"
    audio_path.write_bytes(b"audio")

    transcriber = Mock()
    transcriber.transcribe.return_value = "Обсудили новый релиз"
    generator = Mock()
    generator.generate.return_value = "Готовый отчёт"
    service = ReportService(transcriber=transcriber, generator=generator)

    result = asyncio.run(
        service.generate(
            audio_path=audio_path,
            meeting_date="2026-07-16",
            participants="Иванов Иван",
        )
    )

    assert result == "Готовый отчёт"
    transcriber.transcribe.assert_called_once_with(str(audio_path))
    generator.generate.assert_called_once()
    prompt = generator.generate.call_args.args[0]
    assert "Обсудили новый релиз" in prompt
    assert "Иванов Иван" in prompt
    assert "2026-07-16" in prompt


def test_generate_wraps_transcription_error_and_skips_generator(
    tmp_path: Path,
) -> None:
    original_error = RuntimeError("transcription failed")
    transcriber = Mock()
    transcriber.transcribe.side_effect = original_error
    generator = Mock()
    service = ReportService(transcriber=transcriber, generator=generator)

    with pytest.raises(ReportGenerationError) as error:
        asyncio.run(
            service.generate(
                audio_path=tmp_path / "meeting.wav",
                meeting_date="2026-07-16",
                participants="Иванов Иван",
            )
        )

    assert error.value.__cause__ is original_error
    generator.generate.assert_not_called()


def test_generate_wraps_generator_error(tmp_path: Path) -> None:
    original_error = RuntimeError("generator failed")
    transcriber = Mock()
    transcriber.transcribe.return_value = "Текст встречи"
    generator = Mock()
    generator.generate.side_effect = original_error
    service = ReportService(transcriber=transcriber, generator=generator)

    with pytest.raises(ReportGenerationError) as error:
        asyncio.run(
            service.generate(
                audio_path=tmp_path / "meeting.wav",
                meeting_date="2026-07-16",
                participants="Иванов Иван",
            )
        )

    assert error.value.__cause__ is original_error
