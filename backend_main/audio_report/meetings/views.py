import datetime
import os
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.views import APIView
from .models import Meeting, MeetingEmployee
from .render_docx import render_docx_template
from .send_email import send_report_to_emails
from .serializers import ReportSerializer, ReportInputSerializer
from rest_framework.response import Response
from audio_report.settings import BASE_DIR, MEDIA_ROOT
from employees.models import Employee
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
        list_checked_employee_id = []
        number_emp = 0
        for task_i in data["tasks"]:
            if task_i["employee_id"] not in list_checked_employee_id:
                number_emp+=1
                list_checked_employee_id.append(task_i["employee_id"])
                employee = get_object_or_404(Employee, id=task_i["employee_id"])
                text_task = (f'{number_emp}. '
                             f'{employee.last_name} '
                             f'{employee.first_name} '
                             f'{employee.patronymic if employee.patronymic else ""}\n')

                for task_j in data["tasks"]:
                    if int(task_j["employee_id"]) == employee.id:
                        text_task += f'    – {task_j["content"]} / {task_j["deadline"]}\n'
                tasks_context.append(text_task)

        context = {
            "topic": data["topic"],
            "meeting_date": data["meeting_date"].strftime("%d.%m.%Y"),
            "summary": data["summary"],
            "key_questions": "\n".join(f"– {_}" for _ in data["key_questions"]),
            "participants": ", ".join(
                f"{_['last_name']} {_['first_name']} {_.get('patronymic') or ''}".strip()
                for _ in data["participants"]
            ),
            "tasks": "\n".join(f"{_}" for _ in tasks_context),
            "responsible": next(
                (f"{_['last_name']} {_['first_name']}" for _ in data["participants"]
                 if _["is_responsible"]),
                "Не указан"),
            "now_date": datetime.datetime.now().strftime("%d.%m.%Y"),
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

        list_email_participants = []
        # Связь с участниками
        MeetingEmployee.objects.filter(meeting=meeting).delete()
        for p in data["participants"]:
            employee = get_object_or_404(Employee, id=p["id"])
            list_email_participants.append(employee.email)
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

        # отправляем сообщение
        send_report_to_emails(
            subject="Отчет по совещанию",
            body="Здравствуйте! Во вложении — отчет по итогам совещания.",
            recipient_list=list_email_participants,
            file_path=f"media/reports/{filename}"
        )

        return Response({"report_path": meeting.report_path.name}, status=200)
