from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PostViewSet

# Создаем роутер
router = DefaultRouter()
router.register(r'', PostViewSet, basename='post')

urlpatterns = [
    path('', include(router.urls)),  # Подключаем ViewSet через router
]
