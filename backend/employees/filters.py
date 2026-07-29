import django_filters

from departments.models import Department
from positions.models import Position

from .models import Employee


class EmployeeFilter(django_filters.FilterSet):
    department = django_filters.ModelMultipleChoiceFilter(
        field_name="department",
        queryset=Department.objects.all(),
        label="Отдел",
    )
    position = django_filters.ModelMultipleChoiceFilter(
        field_name="position",
        queryset=Position.objects.all(),
        label="Должность",
    )
    is_active = django_filters.BooleanFilter(
        field_name="is_active",
        label="Активен",
    )

    class Meta:
        model = Employee
        fields = (
            "department",
            "position",
            "is_active",
        )
