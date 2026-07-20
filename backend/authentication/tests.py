from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from departments.models import Department
from employees.models import Employee
from positions.models import Position

PASSWORD = "Strong-Authentication-Test-Password-473!"


class AuthenticationApiTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        department = Department.objects.create(name="Engineering")
        position = Position.objects.create(name="Developer")
        cls.employee = Employee.objects.create_user(
            email="auth-user@example.com",
            password=PASSWORD,
            first_name="Authentication",
            last_name="User",
            department=department,
            position=position,
        )
        cls.inactive_employee = Employee.objects.create_user(
            email="inactive-auth-user@example.com",
            password=PASSWORD,
            first_name="Inactive",
            last_name="User",
            department=department,
            position=position,
            is_active=False,
        )

    def setUp(self):
        self.client = APIClient()

    @property
    def login_url(self):
        return reverse("authentication:token_obtain_pair")

    @property
    def refresh_url(self):
        return reverse("authentication:token_refresh")

    @property
    def logout_url(self):
        return reverse("authentication:token_logout")

    @property
    def verify_url(self):
        return reverse("authentication:token_verify")

    def login(self):
        return self.client.post(
            self.login_url,
            {"email": self.employee.email, "password": PASSWORD},
            format="json",
        )

    def test_login_returns_token_pair_and_user(self):
        response = self.login()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)
        self.assertEqual(response.data["user"]["id"], self.employee.pk)
        self.assertEqual(response.data["user"]["email"], self.employee.email)
        self.assertFalse(response.data["user"]["is_superuser"])

    def test_login_rejects_invalid_password(self):
        response = self.client.post(
            self.login_url,
            {"email": self.employee.email, "password": "Wrong-password"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertNotIn("access", response.data)

    def test_login_rejects_inactive_employee(self):
        response = self.client.post(
            self.login_url,
            {
                "email": self.inactive_employee.email,
                "password": PASSWORD,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_requires_email(self):
        response = self.client.post(
            self.login_url,
            {"password": PASSWORD},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)

    def test_refresh_rotates_refresh_token(self):
        login_response = self.login()
        old_refresh = login_response.data["refresh"]

        response = self.client.post(
            self.refresh_url,
            {"refresh": old_refresh},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)
        self.assertNotEqual(response.data["refresh"], old_refresh)

    def test_rotated_refresh_token_cannot_be_reused(self):
        login_response = self.login()
        old_refresh = login_response.data["refresh"]
        first_refresh_response = self.client.post(
            self.refresh_url,
            {"refresh": old_refresh},
            format="json",
        )
        self.assertEqual(
            first_refresh_response.status_code,
            status.HTTP_200_OK,
        )

        response = self.client.post(
            self.refresh_url,
            {"refresh": old_refresh},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_logout_blacklists_refresh_token(self):
        refresh = self.login().data["refresh"]

        logout_response = self.client.post(
            self.logout_url,
            {"refresh": refresh},
            format="json",
        )
        refresh_response = self.client.post(
            self.refresh_url,
            {"refresh": refresh},
            format="json",
        )

        self.assertEqual(logout_response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            refresh_response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_logout_rejects_invalid_token(self):
        response = self.client.post(
            self.logout_url,
            {"refresh": "invalid-token"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_verify_accepts_valid_access_token(self):
        access = self.login().data["access"]

        response = self.client.post(
            self.verify_url,
            {"token": access},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_verify_rejects_invalid_token(self):
        response = self.client.post(
            self.verify_url,
            {"token": "invalid-token"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
