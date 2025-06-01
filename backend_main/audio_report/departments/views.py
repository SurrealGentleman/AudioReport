from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import Department
from .serializers import DepartmentSerializer


class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    http_method_names = ['get', 'post', 'delete', 'patch']

    def create(self, request, *args, **kwargs):
        # Создаём
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        # Получаем
        all_departments = self.get_queryset()
        response_serializer = self.get_serializer(all_departments, many=True)

        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        # Возвращаем обновлённый список всех пользователей
        all_departments = self.get_queryset()
        all_serializer = self.get_serializer(all_departments, many=True)
        return Response(all_serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        departments = self.get_queryset()
        serializer = self.get_serializer(departments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
