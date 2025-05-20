from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DepartmentViewSet


# Создаем роутер
router = DefaultRouter()
router.register(r'', DepartmentViewSet, basename='department')

urlpatterns = [
    path('', include(router.urls)),  # Подключаем ViewSet через router
]
