from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .filters import EmployeeFilter
from .models import Employee
from .permissions import IsSuperuser
from .serializers import (
    EmployeeAccessSerializer,
    EmployeeCreateSerializer,
    EmployeePasswordSerializer,
    EmployeeReadSerializer,
    EmployeeSelfPasswordSerializer,
    EmployeeUpdateSerializer,
)


class EmployeeViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Employee.objects.select_related(
        "department",
        "position",
    ).order_by(
        "last_name",
        "first_name",
        "id",
    )

    filterset_class = EmployeeFilter

    search_fields = (
        "email",
        "first_name",
        "last_name",
        "patronymic",
    )

    ordering_fields = (
        "email",
        "first_name",
        "last_name",
        "date_joined",
        "last_login",
    )

    ordering = (
        "last_name",
        "first_name",
        "id",
    )

    http_method_names = (
        "get",
        "post",
        "patch",
        "head",
        "options",
    )

    serializer_action_classes = {
        "list": EmployeeReadSerializer,
        "retrieve": EmployeeReadSerializer,
        "create": EmployeeCreateSerializer,
        "partial_update": EmployeeUpdateSerializer,
        "set_password": EmployeePasswordSerializer,
        "change_own_password": EmployeeSelfPasswordSerializer,
        "update_access": EmployeeAccessSerializer,
    }

    superuser_actions = frozenset(
        {
            "create",
            "partial_update",
            "set_password",
            "update_access",
        }
    )

    def get_serializer_class(self):
        return self.serializer_action_classes.get(
            self.action,
            EmployeeReadSerializer,
        )

    def get_permissions(self):
        permission_classes = [IsAuthenticated]

        if self.action in self.superuser_actions:
            permission_classes.append(IsSuperuser)

        return [permission() for permission in permission_classes]

    def create(self, request, *args, **kwargs):
        input_serializer = self.get_serializer(
            data=request.data,
        )
        input_serializer.is_valid(raise_exception=True)

        employee = input_serializer.save()

        output_serializer = EmployeeReadSerializer(
            employee,
            context=self.get_serializer_context(),
        )

        headers = self.get_success_headers(
            output_serializer.data,
        )

        return Response(
            output_serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers,
        )

    def partial_update(self, request, *args, **kwargs):
        employee = self.get_object()

        input_serializer = self.get_serializer(
            employee,
            data=request.data,
            partial=True,
        )
        input_serializer.is_valid(raise_exception=True)

        employee = input_serializer.save()

        output_serializer = EmployeeReadSerializer(
            employee,
            context=self.get_serializer_context(),
        )

        return Response(
            output_serializer.data,
            status=status.HTTP_200_OK,
        )

    @action(
        detail=True,
        methods=["post"],
        url_path="set-password",
    )
    def set_password(self, request, pk=None):
        employee = self.get_object()

        serializer = self.get_serializer(
            employee,
            data=request.data,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            status=status.HTTP_204_NO_CONTENT,
        )

    @action(
        detail=False,
        methods=["post"],
        url_path="me/change-password",
    )
    def change_own_password(self, request):
        serializer = self.get_serializer(
            request.user,
            data=request.data,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            status=status.HTTP_204_NO_CONTENT,
        )

    @action(
        detail=True,
        methods=["patch"],
        url_path="access",
    )
    def update_access(self, request, pk=None):
        employee = self.get_object()

        input_serializer = self.get_serializer(
            employee,
            data=request.data,
            partial=True,
        )
        input_serializer.is_valid(raise_exception=True)

        employee = input_serializer.save()

        output_serializer = EmployeeReadSerializer(
            employee,
            context=self.get_serializer_context(),
        )

        return Response(
            output_serializer.data,
            status=status.HTTP_200_OK,
        )
