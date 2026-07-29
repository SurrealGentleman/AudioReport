from django.contrib import admin
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from departments.models import Department
from employees.models import Employee

from .admin import PositionAdmin
from .models import Position
from .serializers import PositionSerializer

PASSWORD = "Strong-Position-Test-Password-473!"


class PositionModelTests(TestCase):
    def test_string_representation_returns_name(self):
        position = Position(name="Developer")

        self.assertEqual(str(position), "Developer")

    def test_clean_strips_surrounding_whitespace(self):
        position = Position(name="  Developer  ")

        position.full_clean()

        self.assertEqual(position.name, "Developer")

    def test_name_is_case_insensitively_unique_in_database(self):
        Position.objects.create(name="Developer")

        with self.assertRaises(IntegrityError), transaction.atomic():
            Position.objects.create(name="DEVELOPER")


class PositionSerializerTests(TestCase):
    def test_serializer_strips_name(self):
        serializer = PositionSerializer(data={"name": "  Developer  "})

        self.assertTrue(serializer.is_valid(), serializer.errors)
        position = serializer.save()

        self.assertEqual(position.name, "Developer")

    def test_serializer_rejects_blank_name(self):
        serializer = PositionSerializer(data={"name": "   "})

        self.assertFalse(serializer.is_valid())
        self.assertIn("name", serializer.errors)

    def test_serializer_rejects_case_insensitive_duplicate(self):
        Position.objects.create(name="Developer")
        serializer = PositionSerializer(data={"name": "developer"})

        self.assertFalse(serializer.is_valid())
        self.assertIn("name", serializer.errors)

    def test_model_validation_rejects_case_insensitive_duplicate(self):
        Position.objects.create(name="Developer")
        duplicate = Position(name="DEVELOPER")

        with self.assertRaises(ValidationError):
            duplicate.full_clean()


class PositionApiTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.department = Department.objects.create(name="Engineering")
        cls.position = Position.objects.create(name="Developer")
        cls.other_position = Position.objects.create(name="Accountant")

        cls.superuser = Employee.objects.create_superuser(
            email="position-admin@example.com",
            password=PASSWORD,
            first_name="Position",
            last_name="Administrator",
        )
        cls.employee = Employee.objects.create_user(
            email="position-user@example.com",
            password=PASSWORD,
            first_name="Regular",
            last_name="Employee",
            department=cls.department,
            position=cls.position,
        )

    def setUp(self):
        self.client = APIClient()

    @property
    def list_url(self):
        return reverse("positions:position-list")

    def detail_url(self, position):
        return reverse("positions:position-detail", kwargs={"pk": position.pk})

    def test_anonymous_user_cannot_read_positions(self):
        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_employee_can_read_positions(self):
        self.client.force_authenticate(self.employee)

        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)

    def test_regular_employee_cannot_create_position(self):
        self.client.force_authenticate(self.employee)

        response = self.client.post(
            self.list_url,
            {"name": "Manager"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_superuser_can_create_position(self):
        self.client.force_authenticate(self.superuser)

        response = self.client.post(
            self.list_url,
            {"name": "  Manager  "},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["name"], "Manager")
        self.assertTrue(Position.objects.filter(name="Manager").exists())

    def test_regular_employee_cannot_update_position(self):
        self.client.force_authenticate(self.employee)

        response = self.client.patch(
            self.detail_url(self.other_position),
            {"name": "Chief Accountant"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_superuser_can_update_position(self):
        self.client.force_authenticate(self.superuser)

        response = self.client.patch(
            self.detail_url(self.other_position),
            {"name": "Chief Accountant"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.other_position.refresh_from_db()
        self.assertEqual(self.other_position.name, "Chief Accountant")

    def test_superuser_can_delete_unused_position(self):
        unused = Position.objects.create(name="Unused")
        self.client.force_authenticate(self.superuser)

        response = self.client.delete(self.detail_url(unused))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Position.objects.filter(pk=unused.pk).exists())

    def test_used_position_cannot_be_deleted(self):
        self.client.force_authenticate(self.superuser)

        response = self.client.delete(self.detail_url(self.position))

        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(response.data["code"], "position_in_use")
        self.assertTrue(Position.objects.filter(pk=self.position.pk).exists())

    def test_positions_can_be_searched(self):
        self.client.force_authenticate(self.employee)

        response = self.client.get(self.list_url, {"search": "account"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(
            response.data["results"][0]["id"],
            self.other_position.pk,
        )


class PositionAdminTests(TestCase):
    def test_position_uses_custom_admin(self):
        model_admin = admin.site._registry[Position]

        self.assertIsInstance(model_admin, PositionAdmin)
        self.assertEqual(model_admin.search_fields, ("name",))
