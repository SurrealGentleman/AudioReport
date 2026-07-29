import pytest
from fastapi.testclient import TestClient

from app.api.deps import get_report_generator
from app.main import app
from app.services.report_generator import ReportGeneratorUnavailableError


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def test_health_check(client: TestClient) -> None:
    response = client.get("/api/v2/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_liveness_check(client: TestClient) -> None:
    response = client.get("/api/v2/health/live")

    assert response.status_code == 200
    assert response.json() == {"status": "alive"}


def test_readiness_check_returns_ready(client: TestClient) -> None:
    class ReadyGenerator:
        def check_readiness(self) -> None:
            return None

    app.dependency_overrides[get_report_generator] = ReadyGenerator

    response = client.get("/api/v2/health/ready")

    assert response.status_code == 200
    assert response.json() == {"status": "ready"}


def test_readiness_check_returns_503_when_ollama_is_unavailable(
    client: TestClient,
) -> None:
    class UnavailableGenerator:
        def check_readiness(self) -> None:
            raise ReportGeneratorUnavailableError("Ollama unavailable")

    app.dependency_overrides[get_report_generator] = UnavailableGenerator

    response = client.get("/api/v2/health/ready")

    assert response.status_code == 503
    assert response.json() == {"detail": "Service is not ready"}
