import shutil
from datetime import date, timedelta
from pathlib import Path
from unittest.mock import patch
from uuid import uuid4

from django.conf import settings
from django.contrib import admin
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import IntegrityError, transaction
from django.test import TestCase, override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from departments.models import Department
from employees.models import Employee
from positions.models import Position
from tasks.models import Task

from .admin import MeetingAdmin
from .models import Meeting, MeetingEmployee
from .serializers import MeetingUploadSerializer, ReportInputSerializer

PASSWORD = "Strong-Meeting-Test-Password-473!"


class MeetingModelTests(TestCase):
    def test_string_representation_uses_topic(self):
        meeting = Meeting(topic="Architecture review")

        self.assertEqual(str(meeting), "Architecture review")

    def test_string_representation_falls_back_to_id(self):
        meeting = Meeting.objects.create(audio_path="audio/test.wav")

        self.assertEqual(str(meeting), f"Совещание №{meeting.pk}")


class MeetingUploadSerializerTests(TestCase):
    def test_accepts_supported_audio_extension(self):
        serializer = MeetingUploadSerializer(
            data={
                "audio_path": SimpleUploadedFile(
                    "record.wav",
                    b"audio-content",
                    content_type="audio/wav",
                )
            }
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_rejects_unsupported_extension(self):
        serializer = MeetingUploadSerializer(
            data={
                "audio_path": SimpleUploadedFile(
                    "record.exe",
                    b"not-audio",
                )
            }
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("audio_path", serializer.errors)


class MeetingApiTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        department = Department.objects.create(name="Engineering")
        position = Position.objects.create(name="Developer")
        cls.owner = Employee.objects.create_user(
            email="meeting-owner@example.com",
            password=PASSWORD,
            first_name="Meeting",
            last_name="Owner",
            department=department,
            position=position,
        )
        cls.participant = Employee.objects.create_user(
            email="meeting-participant@example.com",
            password=PASSWORD,
            first_name="Meeting",
            last_name="Participant",
            department=department,
            position=position,
        )
        cls.outsider = Employee.objects.create_user(
            email="meeting-outsider@example.com",
            password=PASSWORD,
            first_name="Meeting",
            last_name="Outsider",
            department=department,
            position=position,
        )
        cls.superuser = Employee.objects.create_superuser(
            email="meeting-admin@example.com",
            password=PASSWORD,
            first_name="Meeting",
            last_name="Administrator",
        )
        cls.meeting = Meeting.objects.create(
            topic="Architecture review",
            meeting_date=date.today(),
            audio_path="audio/test.wav",
            created_by=cls.owner,
        )
        MeetingEmployee.objects.create(
            meeting=cls.meeting,
            employee=cls.participant,
            is_responsible=True,
        )

    def setUp(self):
        self.client = APIClient()
        test_media_root = Path(settings.BASE_DIR) / ".test-media"
        test_media_root.mkdir(exist_ok=True)
        self.media_directory = test_media_root / f"meetings-{uuid4().hex}"
        self.media_directory.mkdir()
        self.settings_override = override_settings(
            MEDIA_ROOT=self.media_directory,
        )
        self.settings_override.enable()

    def tearDown(self):
        self.settings_override.disable()
        shutil.rmtree(self.media_directory, ignore_errors=True)

    @property
    def list_url(self):
        return reverse("meetings:meeting-list")

    @property
    def save_url(self):
        return reverse("meetings:report-save")

    def detail_url(self, meeting):
        return reverse("meetings:meeting-detail", kwargs={"pk": meeting.pk})

    def report_payload(self):
        return {
            "meeting_id": self.meeting.pk,
            "topic": "Updated architecture review",
            "meeting_date": date.today().strftime("%d.%m.%Y"),
            "summary": "Summary",
            "key_questions": ["Question one"],
            "participants": [
                {"id": self.participant.pk, "is_responsible": True},
            ],
            "tasks": [
                {
                    "employee_id": self.participant.pk,
                    "content": "Prepare diagram",
                    "deadline": (date.today() + timedelta(days=2)).strftime("%d.%m.%Y"),
                }
            ],
        }

    def test_anonymous_user_cannot_list_meetings(self):
        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_owner_sees_created_meeting(self):
        self.client.force_authenticate(self.owner)

        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_participant_sees_meeting(self):
        self.client.force_authenticate(self.participant)

        response = self.client.get(self.detail_url(self.meeting))

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_outsider_cannot_retrieve_meeting(self):
        self.client.force_authenticate(self.outsider)

        response = self.client.get(self.detail_url(self.meeting))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_superuser_sees_all_meetings(self):
        Meeting.objects.create(
            audio_path="audio/other.wav",
            created_by=self.outsider,
        )
        self.client.force_authenticate(self.superuser)

        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)

    def test_non_owner_cannot_save_report(self):
        self.client.force_authenticate(self.participant)

        response = self.client.post(
            self.save_url,
            self.report_payload(),
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @patch("meetings.services.render_docx_template")
    def test_owner_can_save_report_and_create_linked_task(self, render_mock):
        self.client.force_authenticate(self.owner)

        response = self.client.post(
            self.save_url,
            self.report_payload(),
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.meeting.refresh_from_db()
        task = Task.objects.get(meeting=self.meeting)
        self.assertEqual(task.employee, self.participant)
        self.assertEqual(task.content, "Prepare diagram")
        self.assertTrue(self.meeting.report_path.name.startswith("reports/"))
        render_mock.assert_called_once()

    @patch("meetings.services.render_docx_template")
    def test_repeated_save_replaces_meeting_tasks(self, render_mock):
        self.client.force_authenticate(self.owner)
        payload = self.report_payload()

        first_response = self.client.post(self.save_url, payload, format="json")
        second_response = self.client.post(self.save_url, payload, format="json")

        self.assertEqual(first_response.status_code, status.HTTP_200_OK)
        self.assertEqual(second_response.status_code, status.HTTP_200_OK)
        self.assertEqual(Task.objects.filter(meeting=self.meeting).count(), 1)

    def test_report_rejects_task_for_non_participant(self):
        payload = self.report_payload()
        payload["tasks"][0]["employee_id"] = self.outsider.pk
        serializer = ReportInputSerializer(data=payload)

        self.assertFalse(serializer.is_valid())
        self.assertIn("tasks", serializer.errors)

    def test_report_requires_responsible_participant(self):
        payload = self.report_payload()
        payload["participants"][0]["is_responsible"] = False
        serializer = ReportInputSerializer(data=payload)

        self.assertFalse(serializer.is_valid())
        self.assertIn("participants", serializer.errors)

    def test_duplicate_membership_is_rejected_by_database(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            MeetingEmployee.objects.create(
                meeting=self.meeting,
                employee=self.participant,
            )


class MeetingAdminTests(TestCase):
    def test_meeting_uses_custom_admin(self):
        model_admin = admin.site._registry[Meeting]

        self.assertIsInstance(model_admin, MeetingAdmin)
        self.assertEqual(model_admin.list_select_related, ("created_by",))
