from django.urls import path
from .views import MeetingViewSet, SaveReportView


urlpatterns = [
    path('', MeetingViewSet.as_view({'get': 'list'}), name='view-reports'),
    path('save/', SaveReportView.as_view(), name='save-report')
]
