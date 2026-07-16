import asyncio
import os
from pathlib import Path

import pytest


pytestmark = pytest.mark.integration

if os.getenv("RUN_INTEGRATION_TESTS") != "1":
    pytest.skip(
        "Set RUN_INTEGRATION_TESTS=1 to run integration tests",
        allow_module_level=True,
    )

from app.core.config import settings  # noqa: E402
from app.services.report_generator import Llama  # noqa: E402
from app.services.report_service import ReportService  # noqa: E402
from app.services.transcriber import Whisper  # noqa: E402


def test_ollama_is_ready_and_generates_text() -> None:
    generator = Llama()

    generator.check_readiness()
    response = generator.generate(
        "Ответь одним словом на русском языке: готов."
    )

    assert response.strip()


@pytest.mark.slow
def test_real_audio_report_pipeline() -> None:
    audio_path_value = os.getenv("INTEGRATION_AUDIO_PATH")
    if not audio_path_value:
        pytest.skip("Set INTEGRATION_AUDIO_PATH to a real audio file")

    audio_path = Path(audio_path_value)
    if not audio_path.is_file():
        pytest.fail(f"Integration audio file does not exist: {audio_path}")

    service = ReportService(
        transcriber=Whisper(
            model_name=settings.whisper_model,
            device=settings.device_for_ai,
        ),
        generator=Llama(),
    )

    report = asyncio.run(
        service.generate(
            audio_path=audio_path,
            meeting_date="2026-07-16",
            participants="Тестовый участник",
        )
    )

    assert report.strip()
    assert "**Тема совещания**" in report
