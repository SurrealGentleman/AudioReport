from django.contrib.auth.forms import (
    UserChangeForm,
    UserCreationForm,
)

from .models import Employee


class EmployeeCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = Employee
        fields = (
            "email",
            "first_name",
            "last_name",
            "patronymic",
            "department",
            "position",
            "is_active",
            "is_staff",
            "is_superuser",
        )


class EmployeeChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = Employee
        fields = (
            "email",
            "first_name",
            "last_name",
            "patronymic",
            "department",
            "position",
            "is_active",
            "is_staff",
            "is_superuser",
            "groups",
            "user_permissions",
        )
