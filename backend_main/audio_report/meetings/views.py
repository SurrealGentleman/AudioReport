import datetime
import os
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.views import APIView
from .models import Meeting, MeetingEmployee
from .render_docx import render_docx_template
from .serializers import ReportSerializer, ReportInputSerializer
from rest_framework.response import Response
from audio_report.settings import BASE_DIR, MEDIA_ROOT
from users.models import Employee
from tasks.models import Task


class MeetingViewSet(viewsets.ModelViewSet):
    queryset = Meeting.objects.all()
    http_method_names = ['get']

    def list(self, request, **kwargs):
        employee_id = request.query_params.get('employee_id')
        if not employee_id:
            return Response({'detail': 'employee_id is required'}, status=400)

        meetings = Meeting.objects.filter(meetingemployee__employee__id=employee_id)

        serializer = ReportSerializer(meetings, many=True)
        return Response(serializer.data)


class SaveReportView(APIView):

    def post(self, request):
        serializer = ReportInputSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data

        meeting = get_object_or_404(Meeting, id=data["meeting_id"])

        # Обновляем поля
        meeting.topic = data["topic"]
        meeting.meeting_date = data["meeting_date"]

        tasks_context = []
        for task in data["tasks"]:
            employee = get_object_or_404(Employee, id=task["employee_id"])
            tasks_context.append({
                "content": task["content"],
                "employee": f"{employee.last_name} {employee.first_name}",
                "deadline": task["deadline"]
            })

        context = {
            "topic": data["topic"],
            "summary": data["summary"],
            "key_questions": "\n".join(f"- {q}" for q in data["key_questions"]),
            "participants": ", ".join(
                f"{p['last_name']} {p['first_name']} {p.get('patronymic') or ''}".strip()
                for p in data["participants"]
            ),
            "responsible": next(
                (f"{p['last_name']} {p['first_name']}" for p in data["participants"] if p["is_responsible"]),
                "Не указан"),
            "now_date": datetime.datetime.now().strftime("%d.%m.%Y"),
            "tasks": tasks_context
        }

        template_path = os.path.join(BASE_DIR, "media/templates/meeting_template.docx")

        now_str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"report_{meeting.id}_{now_str}.docx"
        output_dir = os.path.join(MEDIA_ROOT, "reports")
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, filename)

        render_docx_template(template_path, context, output_path)

        # Сохраняем путь
        meeting.report_path.name = f"reports/{filename}"
        meeting.save()

        # Связь с участниками
        MeetingEmployee.objects.filter(meeting=meeting).delete()
        for p in data["participants"]:
            employee = get_object_or_404(Employee, id=p["id"])
            MeetingEmployee.objects.create(
                meeting=meeting,
                employee=employee,
                is_responsible=p["is_responsible"]
            )

        # Добавляем задачи
        if data["tasks"]:
            for task_data in data["tasks"]:
                employee = get_object_or_404(Employee, id=task_data["employee_id"])
                if not employee:
                    continue
                Task.objects.create(
                    content=task_data["content"],
                    due_date=datetime.datetime.strptime(task_data["deadline"], "%d.%m.%Y").date(),
                    employee=employee
                )

        return Response({"report_path": meeting.report_path.name}, status=200)
