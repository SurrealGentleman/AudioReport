from django.db.models import Prefetch, Q
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import mixins, status, viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Meeting, MeetingEmployee
from .serializers import MeetingReadSerializer, ReportInputSerializer
from .services import save_meeting_report


class MeetingViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = MeetingReadSerializer
    permission_classes = (IsAuthenticated,)
    filterset_fields = {
        "meeting_date": ("exact", "gte", "lte"),
    }
    search_fields = ("topic",)
    ordering_fields = ("meeting_date", "report_date", "id")
    ordering = ("-meeting_date", "-id")
    http_method_names = ("get", "head", "options")

    def get_queryset(self):
        memberships = MeetingEmployee.objects.select_related(
            "employee",
            "employee__department",
            "employee__position",
        )
        queryset = Meeting.objects.select_related("created_by").prefetch_related(
            Prefetch("memberships", queryset=memberships),
        )
        user = self.request.user

        if not user.is_authenticated:
            return queryset.none()

        if user.is_superuser:
            employee_id = self.request.query_params.get("employee_id")
            if employee_id:
                queryset = queryset.filter(
                    memberships__employee_id=employee_id,
                )
            return queryset.distinct()

        return queryset.filter(
            Q(created_by=user) | Q(memberships__employee=user),
        ).distinct()


class SaveReportView(APIView):
    permission_classes = (IsAuthenticated,)

    @extend_schema(
        tags=("Reports",),
        summary="Сохранить сформированный отчёт",
        description=(
            "Сохраняет данные отчёта, участников и задачи, формирует DOCX-файл "
            "и возвращает обновлённую встречу."
        ),
        request=ReportInputSerializer,
        responses={
            200: MeetingReadSerializer,
            400: OpenApiResponse(description="Некорректные данные отчёта."),
            401: OpenApiResponse(description="Требуется JWT-аутентификация."),
            403: OpenApiResponse(
                description="Сохранять отчёт может только создатель встречи."
            ),
        },
    )
    def post(self, request):
        serializer = ReportInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        meeting = serializer.validated_data["meeting"]

        if not request.user.is_superuser and meeting.created_by_id != request.user.pk:
            raise PermissionDenied("Сохранять отчёт может только создатель совещания.")

        meeting = save_meeting_report(serializer.validated_data)
        output_serializer = MeetingReadSerializer(
            meeting,
            context={"request": request},
        )

        return Response(output_serializer.data, status=status.HTTP_200_OK)
