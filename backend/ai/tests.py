import json
import shutil
from datetime import date
from pathlib import Path
from unittest.mock import Mock, patch
from uuid import uuid4

import requests
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import SimpleTestCase, TestCase, override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from departments.models import Department
from employees.models import Employee
from meetings.models import Meeting
from positions.models import Position

from .neuro_client import (
    AIInvalidResponseError,
    AIServiceError,
    AIServiceTimeoutError,
    NeuroServerClient,
)
from .parsers import AIReportParseError, parse_ai_report
from .services import generate_meeting_report

PASSWORD = "Strong-AI-Test-Password-473!"

REPORT_TEXT = """\
**Тема совещания**: Архитектура проекта

**Ключевые вопросы**:
- Сроки реализации
- Архитектура API

**Содержание**:
Обсудили дальнейшее развитие проекта.

**Задачи**:
*Иванов Иван Иванович*
- **Задача**: Подготовить схему API **Срок**: 25.07.2026
"""

PARTICIPANTS = [
    {
        "id": 7,
        "first_name": "Иван",
        "last_name": "Иванов",
        "patronymic": "Иванович",
        "is_responsible": True,
    }
]


class AIReportParserTests(SimpleTestCase):
    def test_parses_valid_report(self):
        report = parse_ai_report(REPORT_TEXT, PARTICIPANTS)

        self.assertEqual(report["topic"], "Архитектура проекта")
        self.assertEqual(len(report["key_questions"]), 2)
        self.assertEqual(report["tasks"][0]["employee_id"], 7)
        self.assertEqual(report["tasks"][0]["deadline"], "25.07.2026")

    def test_accepts_short_participant_name(self):
        text = REPORT_TEXT.replace(
            "*Иванов Иван Иванович*",
            "**Иванов Иван**",
        )

        report = parse_ai_report(text, PARTICIPANTS)

        self.assertEqual(report["tasks"][0]["employee_id"], 7)

    def test_rejects_missing_required_sections(self):
        with self.assertRaises(AIReportParseError):
            parse_ai_report("**Тема совещания**: Только тема", PARTICIPANTS)

    def test_rejects_unknown_task_employee(self):
        text = REPORT_TEXT.replace(
            "Иванов Иван Иванович",
            "Петров Пётр Петрович",
        )

        with self.assertRaises(AIReportParseError):
            parse_ai_report(text, PARTICIPANTS)

    def test_rejects_invalid_deadline(self):
        text = REPORT_TEXT.replace("25.07.2026", "к следующей неделе")

        with self.assertRaises(AIReportParseError):
            parse_ai_report(text, PARTICIPANTS)


@override_settings(
    AI_API_URL="https://ai.example.test/generate",
    AI_API_KEY="test-key",
    AI_CONNECT_TIMEOUT=2.0,
    AI_READ_TIMEOUT=30.0,
)
class NeuroServerClientTests(SimpleTestCase):
    def setUp(self):
        self.session = Mock()
        self.client = NeuroServerClient(session=self.session)
        self.audio = SimpleUploadedFile(
            "record.wav",
            b"audio-content",
            content_type="audio/wav",
        )

    def test_returns_json_object(self):
        response = Mock()
        response.json.return_value = {"report_text": REPORT_TEXT}
        self.session.post.return_value = response

        payload = self.client.generate_report(
            self.audio,
            ["Иванов Иван Иванович"],
            "18.07.2026",
        )

        self.assertIn("report_text", payload)
        self.session.post.assert_called_once()
        self.assertEqual(
            self.session.post.call_args.kwargs["timeout"],
            (2.0, 30.0),
        )

    def test_converts_timeout_to_domain_exception(self):
        self.session.post.side_effect = requests.Timeout()

        with self.assertRaises(AIServiceTimeoutError):
            self.client.generate_report(self.audio, ["Employee"], "18.07.2026")

    def test_converts_request_error_to_domain_exception(self):
        self.session.post.side_effect = requests.ConnectionError()

        with self.assertRaises(AIServiceError):
            self.client.generate_report(self.audio, ["Employee"], "18.07.2026")

    def test_rejects_non_object_json(self):
        response = Mock()
        response.json.return_value = ["unexpected"]
        self.session.post.return_value = response

        with self.assertRaises(AIInvalidResponseError):
            self.client.generate_report(self.audio, ["Employee"], "18.07.2026")


class AITestDataMixin:
    @classmethod
    def setUpTestData(cls):
        department = Department.objects.create(name="Engineering")
        position = Position.objects.create(name="Developer")
        cls.employee = Employee.objects.create_user(
            email="ai-user@example.com",
            password=PASSWORD,
            first_name="Иван",
            last_name="Иванов",
            patronymic="Иванович",
            department=department,
            position=position,
        )

    def multipart_payload(self):
        return {
            "audio": SimpleUploadedFile(
                "record.wav",
                b"audio-content",
                content_type="audio/wav",
            ),
            "data": json.dumps(
                {
                    "meeting_date": "2026-07-18",
                    "participants": [
                        {
                            "employee_id": self.employee.pk,
                            "is_responsible": True,
                        }
                    ],
                }
            ),
        }


class GenerateMeetingReportServiceTests(AITestDataMixin, TestCase):
    def setUp(self):
        test_media_root = Path(settings.BASE_DIR) / ".test-media"
        test_media_root.mkdir(exist_ok=True)
        self.media_directory = test_media_root / f"ai-{uuid4().hex}"
        self.media_directory.mkdir()
        self.settings_override = override_settings(
            MEDIA_ROOT=self.media_directory,
        )
        self.settings_override.enable()

    def tearDown(self):
        self.settings_override.disable()
        shutil.rmtree(self.media_directory, ignore_errors=True)

    def test_service_saves_meeting_owned_by_requesting_employee(self):
        client = Mock()
        client.generate_report.return_value = {"report_text": REPORT_TEXT}
        audio = self.multipart_payload()["audio"]
        meeting_data = {
            "meeting_date": date(2026, 7, 18),
            "participants": [
                {"employee": self.employee, "is_responsible": True},
            ],
        }

        report = generate_meeting_report(
            audio,
            meeting_data,
            self.employee,
            client=client,
        )

        meeting = Meeting.objects.get(pk=report["meeting_id"])
        self.assertEqual(meeting.created_by, self.employee)
        self.assertTrue(meeting.audio_path.name.startswith("audio/"))


class GenerateReportApiTests(AITestDataMixin, TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse("ai:generate-report")

    def test_anonymous_user_cannot_generate_report(self):
        response = self.client.post(
            self.url,
            self.multipart_payload(),
            format="multipart",
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    @patch("ai.views.generate_meeting_report")
    def test_returns_generated_report(self, generate_mock):
        generate_mock.return_value = {
            "meeting_id": 10,
            "meeting_date": "18.07.2026",
            "topic": "Архитектура проекта",
            "key_questions": [],
            "summary": "Summary",
            "tasks": [],
            "participants": PARTICIPANTS,
        }
        self.client.force_authenticate(self.employee)

        response = self.client.post(
            self.url,
            self.multipart_payload(),
            format="multipart",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["meeting_id"], 10)
        generate_mock.assert_called_once()

    @patch("ai.views.generate_meeting_report")
    def test_invalid_json_does_not_call_ai_service(self, generate_mock):
        self.client.force_authenticate(self.employee)
        payload = self.multipart_payload()
        payload["data"] = "not-json"

        response = self.client.post(self.url, payload, format="multipart")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        generate_mock.assert_not_called()

    @patch("ai.views.generate_meeting_report")
    def test_timeout_returns_gateway_timeout(self, generate_mock):
        generate_mock.side_effect = AIServiceTimeoutError()
        self.client.force_authenticate(self.employee)

        response = self.client.post(
            self.url,
            self.multipart_payload(),
            format="multipart",
        )

        self.assertEqual(response.status_code, status.HTTP_504_GATEWAY_TIMEOUT)

    @patch("ai.views.generate_meeting_report")
    def test_invalid_ai_report_returns_bad_gateway(self, generate_mock):
        generate_mock.side_effect = AIReportParseError()
        self.client.force_authenticate(self.employee)

        response = self.client.post(
            self.url,
            self.multipart_payload(),
            format="multipart",
        )

        self.assertEqual(response.status_code, status.HTTP_502_BAD_GATEWAY)
