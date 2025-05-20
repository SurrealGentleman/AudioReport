from rest_framework import serializers
from .models import Task
from employees.serializers import EmployeeShortSerializer
from departments.serializers import DepartmentSerializer
from posts.serializers import PostSerializer


class TaskSerializer(serializers.ModelSerializer):
    # employee = EmployeeShortSerializer(read_only=True)
    due_date = serializers.DateField(input_formats=["%d.%m.%Y", "%Y-%m-%d"])

    class Meta:
        model = Task
        # fields = '__all__'
        fields = ["id", "due_date", "content", "assigned_date", "status"]
        # exclude = ['employee']


class TaskStatusUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Task
        fields = ['status']
