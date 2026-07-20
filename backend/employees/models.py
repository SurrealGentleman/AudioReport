from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.utils import timezone


class EmployeeManager(BaseUserManager):
    use_in_migrations = True

    def normalize_employee_email(self, email: str) -> str:
        return self.normalize_email(email).strip().lower()

    def create_user(
        self,
        email: str,
        password: str | None = None,
        department=None,
        position=None,
        **extra_fields,
    ):
        if not email:
            raise ValueError("Email обязателен.")

        if not password:
            raise ValueError("Пароль сотрудника обязателен.")

        is_superuser = extra_fields.get("is_superuser", False)

        if not is_superuser:
            if department is None:
                raise ValueError("Для сотрудника необходимо указать отдел.")

            if position is None:
                raise ValueError("Для сотрудника необходимо указать должность.")

        email = self.normalize_employee_email(email)

        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)

        user = self.model(
            email=email,
            department=department,
            position=position,
            **extra_fields,
        )

        user.set_password(password)

        user.save(using=self._db)
        return user

    def create_superuser(
        self,
        email: str,
        password: str,
        **extra_fields,
    ):
        if not password:
            raise ValueError("Пароль суперпользователя обязателен.")

        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Суперпользователь должен иметь is_staff=True.")

        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Суперпользователь должен иметь is_superuser=True.")

        return self.create_user(
            email=email,
            password=password,
            **extra_fields,
        )


class Employee(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(
        "Email",
        unique=True,
    )

    first_name = models.CharField(
        "Имя",
        max_length=150,
    )
    last_name = models.CharField(
        "Фамилия",
        max_length=150,
    )
    patronymic = models.CharField(
        "Отчество",
        max_length=150,
        blank=True,
        default="",
    )

    department = models.ForeignKey(
        "departments.Department",
        verbose_name="Отдел",
        related_name="employees",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )
    position = models.ForeignKey(
        "positions.Position",
        verbose_name="Должность",
        related_name="employees",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )

    is_active = models.BooleanField(
        "Активен",
        default=True,
    )
    is_staff = models.BooleanField(
        "Доступ к администрированию",
        default=False,
    )

    date_joined = models.DateTimeField(
        "Дата регистрации",
        default=timezone.now,
    )

    objects = EmployeeManager()

    EMAIL_FIELD = "email"
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = [
        "first_name",
        "last_name",
    ]

    class Meta:
        verbose_name = "Сотрудник"
        verbose_name_plural = "Сотрудники"
        ordering = [
            "last_name",
            "first_name",
            "id",
        ]
        constraints = [
            models.CheckConstraint(
                condition=(
                    Q(is_superuser=True)
                    | (Q(department__isnull=False) & Q(position__isnull=False))
                ),
                name="employee_requires_department_and_position",
            ),
        ]

    def clean(self):
        super().clean()
        self.email = type(self).objects.normalize_employee_email(self.email)

        errors = {}

        if not self.is_superuser:
            if self.department_id is None:
                errors["department"] = "Для сотрудника необходимо указать отдел."

            if self.position_id is None:
                errors["position"] = "Для сотрудника необходимо указать должность."

        if errors:
            raise ValidationError(errors)

    def get_full_name(self) -> str:
        return " ".join(
            part
            for part in (
                self.last_name,
                self.first_name,
                self.patronymic,
            )
            if part
        )

    def get_short_name(self) -> str:
        return self.first_name

    def __str__(self) -> str:
        return f"{self.get_full_name()} <{self.email}>"
