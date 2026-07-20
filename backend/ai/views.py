from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.exceptions import APIException
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

from .neuro_client import (
    AIInvalidResponseError,
    AIServiceError,
    AIServiceTimeoutError,
)
from .parsers import AIReportParseError
from .serializers import (
    GenerateReportRequestSerializer,
    GenerateReportResponseSerializer,
)
from .services import generate_meeting_report


class AIUpstreamError(APIException):
    status_code = status.HTTP_502_BAD_GATEWAY
    default_detail = "Сервис обработки аудио временно недоступен."
    default_code = "ai_service_error"


class AIUpstreamTimeout(APIException):
    status_code = status.HTTP_504_GATEWAY_TIMEOUT
    default_detail = "Сервис обработки аудио не ответил вовремя."
    default_code = "ai_service_timeout"


class AIInvalidReportError(APIException):
    status_code = status.HTTP_502_BAD_GATEWAY
    default_detail = "Сервис обработки аудио вернул некорректный отчёт."
    default_code = "ai_invalid_report"


class GenerateReportView(APIView):
    permission_classes = (IsAuthenticated,)
    parser_classes = (MultiPartParser, FormParser)
    throttle_classes = (ScopedRateThrottle,)
    throttle_scope = "ai_generate"

    @extend_schema(
        tags=("AI",),
        summary="Сформировать отчёт по аудиозаписи",
        description=(
            "Принимает аудиофайл и JSON-контекст встречи в multipart/form-data, "
            "передаёт запись AI-сервису и возвращает подготовленные данные отчёта."
        ),
        request=GenerateReportRequestSerializer,
        responses={
            201: GenerateReportResponseSerializer,
            400: OpenApiResponse(description="Некорректные входные данные."),
            401: OpenApiResponse(description="Требуется JWT-аутентификация."),
            502: OpenApiResponse(description="AI-сервис вернул некорректный ответ."),
            504: OpenApiResponse(description="Превышено время ожидания AI-сервиса."),
        },
    )
    def post(self, request):
        serializer = GenerateReportRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            report = generate_meeting_report(
                audio_file=serializer.validated_data["audio"],
                meeting_data=serializer.validated_data["data"],
                creator=request.user,
            )
        except AIServiceTimeoutError as error:
            raise AIUpstreamTimeout from error
        except AIInvalidResponseError as error:
            raise AIInvalidReportError from error
        except AIReportParseError as error:
            raise AIInvalidReportError from error
        except AIServiceError as error:
            raise AIUpstreamError from error

        return Response(report, status=status.HTTP_201_CREATED)
