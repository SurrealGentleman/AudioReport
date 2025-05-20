from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .filters import EmployeeFilter
from .models import Employee
from .serializers import EmployeeSerializer


class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
    permission_classes = [IsAuthenticated]
    filterset_class = EmployeeFilter
    http_method_names = ['get', 'post', 'delete']

    def create(self, request, *args, **kwargs):
        # Создаём нового сотрудника
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        # Получаем всех сотрудников после добавления
        all_employees = self.get_queryset()
        response_serializer = self.get_serializer(all_employees, many=True)

        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    def get_queryset(self):
        queryset = super().get_queryset()
        department_ids = self.request.query_params.getlist('department')
        post_ids = self.request.query_params.getlist('post')

        if department_ids:
            queryset = queryset.filter(department__id__in=department_ids)
        if post_ids:
            queryset = queryset.filter(post__id__in=post_ids)

        return queryset

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()

        remaining_employee = self.get_queryset()
        serializer = self.get_serializer(remaining_employee, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


# class LogoutView(APIView):
#     permission_classes = [permissions.IsAuthenticated]
#
#     def post(self, request):
#         serializer = LogoutSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response(status=status.HTTP_204_NO_CONTENT)