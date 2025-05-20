from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import Task
from .serializers import TaskStatusUpdateSerializer, TaskSerializer


class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    # serializer_class = TaskSerializer
    http_method_names = ['get', 'patch']

    def get_serializer_class(self):
        if self.action in ['update', 'partial_update']:
            return TaskStatusUpdateSerializer
        return TaskSerializer

    def partial_update(self, request, *args, **kwargs):
        task = self.get_object()
        serializer = self.get_serializer(task, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        # Получаем все задачи для этого сотрудника
        employee_tasks = Task.objects.filter(employee=task.employee)
        full_serializer = TaskSerializer(employee_tasks, many=True)
        return Response(full_serializer.data, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        return Response({'detail': 'Use PATCH to update status only.'}, status=405)

    def list(self, request):
        employee_id = request.query_params.get('employee_id')
        if not employee_id:
            return Response({'detail': 'employee_id is required'}, status=400)

        tasks = Task.objects.filter(employee__id=employee_id)
        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data)
