from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/auth/", include("authentication.urls")),
    path("api/v1/employees/", include("employees.urls")),
    path("api/v1/positions/", include("positions.urls")),
    path("api/v1/departments/", include("departments.urls")),
    path("api/v1/tasks/", include("tasks.urls")),
    path("api/v1/reports/", include("meetings.urls")),
    path("api/v1/ai/", include("ai.urls")),
]


if settings.DEBUG:
    urlpatterns += [
        path("api/schema/", SpectacularAPIView.as_view(), name="api-schema"),
        path(
            "api/docs/",
            SpectacularSwaggerView.as_view(url_name="api-schema"),
            name="api-docs",
        ),
        path(
            "api/redoc/",
            SpectacularRedocView.as_view(url_name="api-schema"),
            name="api-redoc",
        ),
        *static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT),
    ]
