from django.urls import path

from .views import GenerateReportView

app_name = "ai"

urlpatterns = [
    path("generate/", GenerateReportView.as_view(), name="generate-report"),
]
