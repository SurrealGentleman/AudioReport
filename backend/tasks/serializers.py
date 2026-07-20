from rest_framework import serializers

from employees.serializers import EmployeeShortSerializer

from .models import Task


class TaskSerializer(serializers.ModelSerializer):
    employee = EmployeeShortSerializer(read_only=True)
    due_date = serializers.DateField(
        input_formats=("%d.%m.%Y", "iso-8601"),
    )

    class Meta:
        model = Task
        fields = (
            "id",
            "content",
            "due_date",
            "assigned_date",
            "status",
            "employee",
            "meeting",
        )
        read_only_fields = fields


class TaskStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ("status",)

    def validate(self, attrs):
        if "status" not in attrs:
            raise serializers.ValidationError({"status": "Это поле обязательно."})
        return attrs
