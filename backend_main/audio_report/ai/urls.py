from django.urls import path
from .views import GenerateReportView


urlpatterns = [
    # path('v1/', ChatView.as_view(), name='chat'),
    # path('v2/', TranscribeView.as_view(), name='transcribe'),
    path('generate/', GenerateReportView.as_view(), name='generate-report'),
]
