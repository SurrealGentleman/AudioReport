from django.db.models.deletion import ProtectedError
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Position
from .permissions import IsActiveSuperuserOrReadOnly
from .serializers import PositionSerializer


class PositionViewSet(viewsets.ModelViewSet):
    queryset = Position.objects.order_by("name", "id")
    serializer_class = PositionSerializer
    permission_classes = (IsAuthenticated, IsActiveSuperuserOrReadOnly)
    search_fields = ("name",)
    ordering_fields = ("name", "id")
    ordering = ("name", "id")
    http_method_names = (
        "get",
        "post",
        "patch",
        "delete",
        "head",
        "options",
    )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        try:
            self.perform_destroy(instance)
        except ProtectedError:
            return Response(
                {
                    "detail": (
                        "Нельзя удалить должность, пока она назначена сотрудникам."
                    ),
                    "code": "position_in_use",
                },
                status=status.HTTP_409_CONFLICT,
            )
        return Response(status=status.HTTP_204_NO_CONTENT)
