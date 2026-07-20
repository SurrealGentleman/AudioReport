from django.contrib import admin
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from employees.models import Employee
from positions.models import Position

from .admin import DepartmentAdmin
from .models import Department
from .serializers import DepartmentSerializer

PASSWORD = "Strong-Department-Test-Password-473!"


class DepartmentModelTests(TestCase):
    def test_string_representation_returns_name(self):
        department = Department(name="Engineering")

        self.assertEqual(str(department), "Engineering")

    def test_clean_strips_surrounding_whitespace(self):
        department = Department(name="  Engineering  ")

        department.full_clean()

        self.assertEqual(department.name, "Engineering")

    def test_name_is_case_insensitively_unique_in_database(self):
        Department.objects.create(name="Engineering")

        with self.assertRaises(IntegrityError), transaction.atomic():
            Department.objects.create(name="ENGINEERING")


class DepartmentSerializerTests(TestCase):
    def test_serializer_strips_name(self):
        serializer = DepartmentSerializer(
            data={"name": "  Engineering  "},
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)
        department = serializer.save()

        self.assertEqual(department.name, "Engineering")

    def test_serializer_rejects_blank_name(self):
        serializer = DepartmentSerializer(data={"name": "   "})

        self.assertFalse(serializer.is_valid())
        self.assertIn("name", serializer.errors)

    def test_serializer_rejects_case_insensitive_duplicate(self):
        Department.objects.create(name="Engineering")
        serializer = DepartmentSerializer(
            data={"name": "engineering"},
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("name", serializer.errors)

    def test_model_validation_rejects_case_insensitive_duplicate(self):
        Department.objects.create(name="Engineering")
        duplicate = Department(name="ENGINEERING")

        with self.assertRaises(ValidationError):
            duplicate.full_clean()


class DepartmentApiTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.department = Department.objects.create(name="Engineering")
        cls.other_department = Department.objects.create(name="Finance")
        cls.position = Position.objects.create(name="Developer")

        cls.superuser = Employee.objects.create_superuser(
            email="department-admin@example.com",
            password=PASSWORD,
            first_name="Department",
            last_name="Administrator",
        )
        cls.employee = Employee.objects.create_user(
            email="department-user@example.com",
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
        return reverse("departments:department-list")

    def detail_url(self, department):
        return reverse(
            "departments:department-detail",
            kwargs={"pk": department.pk},
        )

    def test_anonymous_user_cannot_read_departments(self):
        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_employee_can_read_departments(self):
        self.client.force_authenticate(self.employee)

        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)

    def test_regular_employee_cannot_create_department(self):
        self.client.force_authenticate(self.employee)

        response = self.client.post(
            self.list_url,
            {"name": "Legal"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_superuser_can_create_department(self):
        self.client.force_authenticate(self.superuser)

        response = self.client.post(
            self.list_url,
            {"name": "  Legal  "},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["name"], "Legal")
        self.assertTrue(Department.objects.filter(name="Legal").exists())

    def test_regular_employee_cannot_update_department(self):
        self.client.force_authenticate(self.employee)

        response = self.client.patch(
            self.detail_url(self.other_department),
            {"name": "Accounting"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_superuser_can_update_department(self):
        self.client.force_authenticate(self.superuser)

        response = self.client.patch(
            self.detail_url(self.other_department),
            {"name": "Accounting"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.other_department.refresh_from_db()
        self.assertEqual(self.other_department.name, "Accounting")

    def test_superuser_can_delete_unused_department(self):
        unused = Department.objects.create(name="Unused")
        self.client.force_authenticate(self.superuser)

        response = self.client.delete(self.detail_url(unused))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Department.objects.filter(pk=unused.pk).exists())

    def test_used_department_cannot_be_deleted(self):
        self.client.force_authenticate(self.superuser)

        response = self.client.delete(self.detail_url(self.department))

        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(response.data["code"], "department_in_use")
        self.assertTrue(Department.objects.filter(pk=self.department.pk).exists())

    def test_departments_can_be_searched(self):
        self.client.force_authenticate(self.employee)

        response = self.client.get(
            self.list_url,
            {"search": "finance"},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(
            response.data["results"][0]["id"],
            self.other_department.pk,
        )


class DepartmentAdminTests(TestCase):
    def test_department_uses_custom_admin(self):
        model_admin = admin.site._registry[Department]

        self.assertIsInstance(model_admin, DepartmentAdmin)
        self.assertEqual(model_admin.search_fields, ("name",))
