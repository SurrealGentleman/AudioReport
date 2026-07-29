from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from departments.models import Department
from positions.models import Position

from .models import Employee
from .serializers import (
    EmployeeAccessSerializer,
    EmployeeCreateSerializer,
    EmployeeSelfPasswordSerializer,
    EmployeeUpdateSerializer,
)

USER_PASSWORD = "Strong-Test-Password-938!"
NEW_PASSWORD = "Another-Strong-Password-527!"


class EmployeeFixtureMixin:
    @classmethod
    def setUpTestData(cls):
        cls.department = Department.objects.create(name="Engineering")
        cls.other_department = Department.objects.create(name="Finance")
        cls.position = Position.objects.create(name="Developer")
        cls.other_position = Position.objects.create(name="Accountant")

        cls.superuser = Employee.objects.create_superuser(
            email="admin@example.com",
            password=USER_PASSWORD,
            first_name="System",
            last_name="Administrator",
        )
        cls.employee = Employee.objects.create_user(
            email="employee@example.com",
            password=USER_PASSWORD,
            first_name="Ivan",
            last_name="Ivanov",
            patronymic="Ivanovich",
            department=cls.department,
            position=cls.position,
        )


class EmployeeManagerAndModelTests(EmployeeFixtureMixin, TestCase):
    def test_create_user_normalizes_email_and_hashes_password(self):
        employee = Employee.objects.create_user(
            email="  SECOND.USER@Example.COM  ",
            password=USER_PASSWORD,
            first_name="Petr",
            last_name="Petrov",
            department=self.department,
            position=self.position,
        )

        self.assertEqual(employee.email, "second.user@example.com")
        self.assertTrue(employee.check_password(USER_PASSWORD))
        self.assertNotEqual(employee.password, USER_PASSWORD)
        self.assertTrue(employee.is_active)
        self.assertFalse(employee.is_staff)
        self.assertFalse(employee.is_superuser)

    def test_regular_user_requires_department(self):
        with self.assertRaisesMessage(
            ValueError,
            "Для сотрудника необходимо указать отдел.",
        ):
            Employee.objects.create_user(
                email="without-department@example.com",
                password=USER_PASSWORD,
                first_name="Petr",
                last_name="Petrov",
                position=self.position,
            )

    def test_regular_user_requires_position(self):
        with self.assertRaisesMessage(
            ValueError,
            "Для сотрудника необходимо указать должность.",
        ):
            Employee.objects.create_user(
                email="without-position@example.com",
                password=USER_PASSWORD,
                first_name="Petr",
                last_name="Petrov",
                department=self.department,
            )

    def test_regular_user_requires_password(self):
        with self.assertRaisesMessage(
            ValueError,
            "Пароль сотрудника обязателен.",
        ):
            Employee.objects.create_user(
                email="without-password@example.com",
                first_name="Petr",
                last_name="Petrov",
                department=self.department,
                position=self.position,
            )

    def test_superuser_does_not_require_department_or_position(self):
        self.assertIsNone(self.superuser.department)
        self.assertIsNone(self.superuser.position)
        self.assertTrue(self.superuser.is_active)
        self.assertTrue(self.superuser.is_staff)
        self.assertTrue(self.superuser.is_superuser)
        self.assertTrue(self.superuser.check_password(USER_PASSWORD))

    def test_superuser_flags_cannot_be_false(self):
        with self.assertRaisesMessage(
            ValueError,
            "Суперпользователь должен иметь is_staff=True.",
        ):
            Employee.objects.create_superuser(
                email="invalid-admin@example.com",
                password=USER_PASSWORD,
                first_name="Invalid",
                last_name="Admin",
                is_staff=False,
            )

    def test_model_clean_rejects_regular_user_without_work_fields(self):
        employee = Employee(
            email="invalid@example.com",
            first_name="Invalid",
            last_name="Employee",
            is_superuser=False,
        )
        employee.set_password(USER_PASSWORD)

        with self.assertRaises(ValidationError) as error:
            employee.full_clean()

        self.assertIn("department", error.exception.message_dict)
        self.assertIn("position", error.exception.message_dict)

    def test_database_constraint_rejects_regular_user_without_work_fields(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            Employee.objects.create(
                email="constraint@example.com",
                password="not-used-for-authentication",
                first_name="Invalid",
                last_name="Employee",
                is_superuser=False,
            )

    def test_get_full_name_skips_empty_patronymic(self):
        self.employee.patronymic = ""

        self.assertEqual(self.employee.get_full_name(), "Ivanov Ivan")
        self.assertEqual(self.employee.get_short_name(), "Ivan")


class EmployeeSerializerTests(EmployeeFixtureMixin, TestCase):
    def valid_create_payload(self, **overrides):
        payload = {
            "email": "new.employee@example.com",
            "password": NEW_PASSWORD,
            "first_name": "Anna",
            "last_name": "Smirnova",
            "patronymic": "Petrovna",
            "department_id": self.department.pk,
            "position_id": self.position.pk,
        }
        payload.update(overrides)
        return payload

    def test_create_serializer_creates_user_with_hashed_password(self):
        serializer = EmployeeCreateSerializer(
            data=self.valid_create_payload(),
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)
        employee = serializer.save()

        self.assertTrue(employee.check_password(NEW_PASSWORD))
        self.assertEqual(employee.department, self.department)
        self.assertEqual(employee.position, self.position)
        self.assertNotIn("password", serializer.data)

    def test_create_serializer_requires_department_and_position(self):
        payload = self.valid_create_payload()
        payload.pop("department_id")
        payload.pop("position_id")
        serializer = EmployeeCreateSerializer(data=payload)

        self.assertFalse(serializer.is_valid())
        self.assertIn("department_id", serializer.errors)
        self.assertIn("position_id", serializer.errors)

    def test_create_serializer_rejects_case_insensitive_duplicate_email(self):
        serializer = EmployeeCreateSerializer(
            data=self.valid_create_payload(
                email="EMPLOYEE@EXAMPLE.COM",
            ),
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("email", serializer.errors)

    def test_create_serializer_rejects_weak_password(self):
        serializer = EmployeeCreateSerializer(
            data=self.valid_create_payload(password="123"),
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("password", serializer.errors)

    def test_update_serializer_allows_partial_update(self):
        serializer = EmployeeUpdateSerializer(
            self.employee,
            data={"last_name": "Sidorov"},
            partial=True,
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)
        employee = serializer.save()

        self.assertEqual(employee.last_name, "Sidorov")
        self.assertEqual(employee.department, self.department)
        self.assertEqual(employee.position, self.position)

    def test_update_serializer_rejects_null_department(self):
        serializer = EmployeeUpdateSerializer(
            self.employee,
            data={"department_id": None},
            partial=True,
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("department_id", serializer.errors)

    def test_self_password_serializer_requires_current_password(self):
        serializer = EmployeeSelfPasswordSerializer(
            self.employee,
            data={
                "current_password": "Wrong-Password-123!",
                "new_password": NEW_PASSWORD,
            },
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("current_password", serializer.errors)

    def test_access_serializer_prevents_self_deactivation(self):
        request = type("Request", (), {"user": self.superuser})()
        serializer = EmployeeAccessSerializer(
            self.superuser,
            data={"is_active": False},
            partial=True,
            context={"request": request},
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("is_active", serializer.errors)


class EmployeeApiTests(EmployeeFixtureMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.second_employee = Employee.objects.create_user(
            email="accountant@example.com",
            password=USER_PASSWORD,
            first_name="Olga",
            last_name="Petrova",
            department=cls.other_department,
            position=cls.other_position,
        )

    def setUp(self):
        self.client = APIClient()

    @property
    def list_url(self):
        return reverse("employees:employee-list")

    def detail_url(self, employee):
        return reverse(
            "employees:employee-detail",
            kwargs={"pk": employee.pk},
        )

    def test_anonymous_user_cannot_list_employees(self):
        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_user_can_list_employees(self):
        self.client.force_authenticate(self.employee)

        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 3)

    def test_list_can_be_filtered_by_department(self):
        self.client.force_authenticate(self.employee)

        response = self.client.get(
            self.list_url,
            {"department": [self.department.pk]},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        returned_ids = {item["id"] for item in response.data["results"]}
        self.assertEqual(returned_ids, {self.employee.pk})

    def test_list_can_be_searched(self):
        self.client.force_authenticate(self.employee)

        response = self.client.get(
            self.list_url,
            {"search": "accountant"},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(
            response.data["results"][0]["id"],
            self.second_employee.pk,
        )

    def test_regular_user_cannot_create_employee(self):
        self.client.force_authenticate(self.employee)

        response = self.client.post(
            self.list_url,
            self.create_payload(),
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_superuser_can_create_employee(self):
        self.client.force_authenticate(self.superuser)

        response = self.client.post(
            self.list_url,
            self.create_payload(),
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertNotIn("password", response.data)
        created = Employee.objects.get(email="created@example.com")
        self.assertTrue(created.check_password(NEW_PASSWORD))
        self.assertEqual(response.data["id"], created.pk)

    def test_regular_user_cannot_update_employee(self):
        self.client.force_authenticate(self.employee)

        response = self.client.patch(
            self.detail_url(self.second_employee),
            {"last_name": "Changed"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_superuser_can_update_employee(self):
        self.client.force_authenticate(self.superuser)

        response = self.client.patch(
            self.detail_url(self.employee),
            {"last_name": "Changed"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.employee.refresh_from_db()
        self.assertEqual(self.employee.last_name, "Changed")
        self.assertEqual(response.data["last_name"], "Changed")

    def test_delete_method_is_not_available(self):
        self.client.force_authenticate(self.superuser)

        response = self.client.delete(
            self.detail_url(self.employee),
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_405_METHOD_NOT_ALLOWED,
        )

    def test_employee_can_change_own_password(self):
        self.client.force_authenticate(self.employee)
        url = reverse("employees:employee-change-own-password")

        response = self.client.post(
            url,
            {
                "current_password": USER_PASSWORD,
                "new_password": NEW_PASSWORD,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.employee.refresh_from_db()
        self.assertTrue(self.employee.check_password(NEW_PASSWORD))

    def test_regular_user_cannot_set_another_employee_password(self):
        self.client.force_authenticate(self.employee)
        url = reverse(
            "employees:employee-set-password",
            kwargs={"pk": self.second_employee.pk},
        )

        response = self.client.post(
            url,
            {"new_password": NEW_PASSWORD},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_superuser_can_set_employee_password(self):
        self.client.force_authenticate(self.superuser)
        url = reverse(
            "employees:employee-set-password",
            kwargs={"pk": self.employee.pk},
        )

        response = self.client.post(
            url,
            {"new_password": NEW_PASSWORD},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.employee.refresh_from_db()
        self.assertTrue(self.employee.check_password(NEW_PASSWORD))

    def test_superuser_can_deactivate_employee(self):
        self.client.force_authenticate(self.superuser)
        url = reverse(
            "employees:employee-update-access",
            kwargs={"pk": self.employee.pk},
        )

        response = self.client.patch(
            url,
            {"is_active": False},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.employee.refresh_from_db()
        self.assertFalse(self.employee.is_active)

    def test_superuser_cannot_deactivate_self(self):
        self.client.force_authenticate(self.superuser)
        url = reverse(
            "employees:employee-update-access",
            kwargs={"pk": self.superuser.pk},
        )

        response = self.client.patch(
            url,
            {"is_active": False},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.superuser.refresh_from_db()
        self.assertTrue(self.superuser.is_active)

    def create_payload(self):
        return {
            "email": "created@example.com",
            "password": NEW_PASSWORD,
            "first_name": "Created",
            "last_name": "Employee",
            "patronymic": "Test",
            "department_id": self.department.pk,
            "position_id": self.position.pk,
        }
