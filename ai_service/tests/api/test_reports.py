from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.api.deps import get_report_service
from app.api import upload as upload_module
from app.api.v2.endpoints import reports as reports_module
from app.core.config import settings
from app.main import app
from app.services.report_service import ReportGenerationError


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def auth_headers() -> dict[str, str]:
    return {"X-API-Key": settings.api_key}


def test_generate_report_uses_overridden_service_and_removes_temp_file(
    client: TestClient,
) -> None:
    class FakeReportService:
        received_path: Path | None = None
        received_date: str | None = None
        received_participants: str | None = None

        async def generate(
            self,
            audio_path: Path,
            meeting_date: str,
            participants: str,
        ) -> str:
            assert audio_path.exists()
            assert audio_path.read_bytes() == b"fake audio"
            self.received_path = audio_path
            self.received_date = meeting_date
            self.received_participants = participants
            return "Готовый отчёт"

    service = FakeReportService()
    app.dependency_overrides[get_report_service] = lambda: service

    response = client.post(
        "/api/v2/reports/generate",
        headers=auth_headers(),
        files={"audio": ("meeting.wav", b"fake audio", "audio/wav")},
        data={
            "meeting_date": "2026-07-16",
            "participants": "Иванов Иван",
        },
    )

    assert response.status_code == 200
    assert response.json() == {"report_text": "Готовый отчёт"}
    assert service.received_date == "2026-07-16"
    assert service.received_participants == "Иванов Иван"
    assert service.received_path is not None
    assert not service.received_path.exists()


def test_generate_report_returns_401_without_api_key(client: TestClient) -> None:
    app.dependency_overrides[get_report_service] = lambda: object()

    response = client.post(
        "/api/v2/reports/generate",
        files={"audio": ("meeting.wav", b"fake audio", "audio/wav")},
        data={
            "meeting_date": "2026-07-16",
            "participants": "Иванов Иван",
        },
    )

    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid API Key"}


def test_generate_report_returns_401_for_invalid_api_key(
    client: TestClient,
) -> None:
    app.dependency_overrides[get_report_service] = lambda: object()

    response = client.post(
        "/api/v2/reports/generate",
        headers={"X-API-Key": "wrong-key"},
        files={"audio": ("meeting.wav", b"fake audio", "audio/wav")},
        data={
            "meeting_date": "2026-07-16",
            "participants": "Иванов Иван",
        },
    )

    assert response.status_code == 401


def test_generate_report_maps_service_error_and_removes_temp_file(
    client: TestClient,
) -> None:
    class FailingReportService:
        received_path: Path | None = None

        async def generate(
            self,
            audio_path: Path,
            meeting_date: str,
            participants: str,
        ) -> str:
            self.received_path = audio_path
            raise ReportGenerationError("generation failed")

    service = FailingReportService()
    app.dependency_overrides[get_report_service] = lambda: service

    response = client.post(
        "/api/v2/reports/generate",
        headers=auth_headers(),
        files={"audio": ("meeting.wav", b"fake audio", "audio/wav")},
        data={
            "meeting_date": "2026-07-16",
            "participants": "Иванов Иван",
        },
    )

    assert response.status_code == 500
    assert response.json() == {"detail": "Failed to generate report"}
    assert service.received_path is not None
    assert not service.received_path.exists()


def test_generate_report_returns_415_for_unsupported_audio(
    client: TestClient,
) -> None:
    app.dependency_overrides[get_report_service] = lambda: object()

    response = client.post(
        "/api/v2/reports/generate",
        headers=auth_headers(),
        files={"audio": ("meeting.txt", b"not audio", "text/plain")},
        data={
            "meeting_date": "2026-07-16",
            "participants": "Иванов Иван",
        },
    )

    assert response.status_code == 415
    assert response.json() == {"detail": "Unsupported audio format"}


def test_generate_report_returns_400_for_empty_audio(
    client: TestClient,
) -> None:
    app.dependency_overrides[get_report_service] = lambda: object()

    response = client.post(
        "/api/v2/reports/generate",
        headers=auth_headers(),
        files={"audio": ("meeting.wav", b"", "audio/wav")},
        data={
            "meeting_date": "2026-07-16",
            "participants": "Иванов Иван",
        },
    )

    assert response.status_code == 400
    assert response.json() == {"detail": "Audio file is empty"}


def test_generate_report_returns_413_for_oversized_audio(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    app.dependency_overrides[get_report_service] = lambda: object()

    async def save_with_small_limit(upload):
        return await upload_module.save_upload_to_temp(
            upload,
            max_size_bytes=4,
        )

    monkeypatch.setattr(
        reports_module,
        "save_upload_to_temp",
        save_with_small_limit,
    )

    response = client.post(
        "/api/v2/reports/generate",
        headers=auth_headers(),
        files={"audio": ("meeting.wav", b"12345", "audio/wav")},
        data={
            "meeting_date": "2026-07-16",
            "participants": "Иванов Иван",
        },
    )

    assert response.status_code == 413
    assert response.json() == {"detail": "Audio file is too large"}


@pytest.mark.parametrize("missing_field", ["audio", "meeting_date", "participants"])
def test_generate_report_returns_422_for_missing_required_field(
    client: TestClient,
    missing_field: str,
) -> None:
    app.dependency_overrides[get_report_service] = lambda: object()
    files = {"audio": ("meeting.wav", b"fake audio", "audio/wav")}
    data = {
        "meeting_date": "2026-07-16",
        "participants": "Иванов Иван",
    }
    files.pop(missing_field, None)
    data.pop(missing_field, None)

    response = client.post(
        "/api/v2/reports/generate",
        headers=auth_headers(),
        files=files,
        data=data,
    )

    assert response.status_code == 422


def test_generate_report_returns_422_for_invalid_date(client: TestClient) -> None:
    app.dependency_overrides[get_report_service] = lambda: object()

    response = client.post(
        "/api/v2/reports/generate",
        headers=auth_headers(),
        files={"audio": ("meeting.wav", b"fake audio", "audio/wav")},
        data={
            "meeting_date": "16.07.2026",
            "participants": "Иванов Иван",
        },
    )

    assert response.status_code == 422


def test_generate_report_returns_422_for_blank_participants(
    client: TestClient,
) -> None:
    app.dependency_overrides[get_report_service] = lambda: object()

    response = client.post(
        "/api/v2/reports/generate",
        headers=auth_headers(),
        files={"audio": ("meeting.wav", b"fake audio", "audio/wav")},
        data={
            "meeting_date": "2026-07-16",
            "participants": "   ",
        },
    )

    assert response.status_code == 422
