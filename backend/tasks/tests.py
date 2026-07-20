from datetime import date, timedelta

from django.contrib import admin
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from departments.models import Department
from employees.models import Employee
from positions.models import Position

from .admin import TaskAdmin
from .models import Task

PASSWORD = "Strong-Task-Test-Password-473!"


class TaskModelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        department = Department.objects.create(name="Engineering")
        position = Position.objects.create(name="Developer")
        cls.employee = Employee.objects.create_user(
            email="task-model@example.com",
            password=PASSWORD,
            first_name="Task",
            last_name="Employee",
            department=department,
            position=position,
        )

    def test_string_representation_is_truncated(self):
        task = Task(content="A" * 60, due_date=date.today())

        self.assertEqual(str(task), f"{'A' * 47}...")
        self.assertEqual(len(str(task)), 50)

    def test_clean_strips_content(self):
        task = Task(content="  Prepare report  ", due_date=date.today())

        task.full_clean()

        self.assertEqual(task.content, "Prepare report")

    def test_clean_rejects_blank_content(self):
        task = Task(content="   ", due_date=date.today())

        with self.assertRaises(ValidationError):
            task.full_clean()

    def test_database_rejects_empty_content(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            Task.objects.create(content="", due_date=date.today())

    def test_deleting_employee_preserves_task(self):
        task = Task.objects.create(
            content="Prepare report",
            due_date=date.today(),
            employee=self.employee,
        )

        self.employee.delete()
        task.refresh_from_db()

        self.assertIsNone(task.employee)


class TaskApiTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        department = Department.objects.create(name="Engineering")
        position = Position.objects.create(name="Developer")
        cls.employee = Employee.objects.create_user(
            email="task-owner@example.com",
            password=PASSWORD,
            first_name="Task",
            last_name="Owner",
            department=department,
            position=position,
        )
        cls.other_employee = Employee.objects.create_user(
            email="other-task-owner@example.com",
            password=PASSWORD,
            first_name="Other",
            last_name="Owner",
            department=department,
            position=position,
        )
        cls.superuser = Employee.objects.create_superuser(
            email="task-admin@example.com",
            password=PASSWORD,
            first_name="Task",
            last_name="Administrator",
        )
        cls.task = Task.objects.create(
            content="Prepare report",
            due_date=date.today() + timedelta(days=2),
            employee=cls.employee,
        )
        cls.other_task = Task.objects.create(
            content="Approve budget",
            due_date=date.today() + timedelta(days=3),
            employee=cls.other_employee,
        )

    def setUp(self):
        self.client = APIClient()

    @property
    def list_url(self):
        return reverse("tasks:task-list")

    def detail_url(self, task):
        return reverse("tasks:task-detail", kwargs={"pk": task.pk})

    def test_anonymous_user_cannot_read_tasks(self):
        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_employee_sees_only_own_tasks(self):
        self.client.force_authenticate(self.employee)

        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["id"], self.task.pk)

    def test_employee_cannot_retrieve_another_employees_task(self):
        self.client.force_authenticate(self.employee)

        response = self.client.get(self.detail_url(self.other_task))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_employee_can_update_own_task_status(self):
        self.client.force_authenticate(self.employee)

        response = self.client.patch(
            self.detail_url(self.task),
            {"status": True},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.task.refresh_from_db()
        self.assertTrue(self.task.status)

    def test_employee_cannot_update_another_employees_task(self):
        self.client.force_authenticate(self.employee)

        response = self.client.patch(
            self.detail_url(self.other_task),
            {"status": True},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_patch_rejects_fields_other_than_status(self):
        self.client.force_authenticate(self.employee)

        response = self.client.patch(
            self.detail_url(self.task),
            {"content": "Changed"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.task.refresh_from_db()
        self.assertEqual(self.task.content, "Prepare report")

    def test_put_is_not_allowed(self):
        self.client.force_authenticate(self.employee)

        response = self.client.put(
            self.detail_url(self.task),
            {"status": True},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_405_METHOD_NOT_ALLOWED,
        )

    def test_superuser_sees_all_tasks(self):
        self.client.force_authenticate(self.superuser)

        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)

    def test_superuser_can_filter_by_employee_id(self):
        self.client.force_authenticate(self.superuser)

        response = self.client.get(
            self.list_url,
            {"employee_id": self.other_employee.pk},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(
            response.data["results"][0]["id"],
            self.other_task.pk,
        )

    def test_tasks_can_be_filtered_by_status(self):
        self.task.status = True
        self.task.save(update_fields=("status",))
        self.client.force_authenticate(self.superuser)

        response = self.client.get(self.list_url, {"status": "true"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["id"], self.task.pk)

    def test_tasks_can_be_searched(self):
        self.client.force_authenticate(self.superuser)

        response = self.client.get(self.list_url, {"search": "budget"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(
            response.data["results"][0]["id"],
            self.other_task.pk,
        )


class TaskAdminTests(TestCase):
    def test_task_uses_custom_admin(self):
        model_admin = admin.site._registry[Task]

        self.assertIsInstance(model_admin, TaskAdmin)
        self.assertEqual(
            model_admin.list_select_related,
            ("employee", "meeting"),
        )
