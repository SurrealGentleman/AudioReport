from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView

from audio_report import settings
# from employees.views import LogoutView
from auth.views import CustomTokenObtainPairView

urlpatterns = [
    path("api/token/", CustomTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    # path('api/logout/', LogoutView.as_view(), name='logout'),

    path('admin/', admin.site.urls),
    path('api/employees/', include('employees.urls')),
    path('api/posts/', include('posts.urls')),
    path('api/departments/', include('departments.urls')),
    path('api/tasks/', include('tasks.urls')),

    path('api/reports/', include('meetings.urls')),

    path('api/ai/v1/', include('ai.urls')),
]

# Подключаем раздачу статики в режиме DEBUG
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
