from rest_framework import mixins, viewsets
from rest_framework.permissions import IsAuthenticated

from .models import Task
from .serializers import TaskSerializer, TaskStatusUpdateSerializer


class TaskViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = TaskSerializer
    permission_classes = (IsAuthenticated,)
    filterset_fields = {
        "status": ("exact",),
        "due_date": ("exact", "gte", "lte"),
    }
    search_fields = ("content",)
    ordering_fields = ("due_date", "assigned_date", "status", "id")
    ordering = ("status", "due_date", "id")
    http_method_names = ("get", "patch", "head", "options")

    def get_queryset(self):
        queryset = Task.objects.select_related(
            "employee",
            "employee__department",
            "employee__position",
            "meeting",
        )
        user = self.request.user

        if not user.is_authenticated:
            return queryset.none()

        if not user.is_superuser:
            return queryset.filter(employee=user)

        employee_id = self.request.query_params.get("employee_id")
        if employee_id:
            queryset = queryset.filter(employee_id=employee_id)

        return queryset

    def get_serializer_class(self):
        if self.action == "partial_update":
            return TaskStatusUpdateSerializer
        return TaskSerializer
