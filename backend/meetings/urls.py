from django.urls import path
from rest_framework.routers import SimpleRouter

from .views import MeetingViewSet, SaveReportView

app_name = "meetings"

router = SimpleRouter()
router.register("", MeetingViewSet, basename="meeting")

urlpatterns = [
    path("save/", SaveReportView.as_view(), name="report-save"),
    *router.urls,
]
