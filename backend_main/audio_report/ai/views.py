import datetime as dt
import json
import re
import requests
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from ai.neuro_client import NeuroServerClient
from employees.models import Employee
from meetings.serializers import MeetingSerializer
from audio_report.settings import env


class GenerateReportView(APIView):

    def post(self, request):
        audio_file = request.FILES.get("audio")
        data = request.POST.get("data")

        processed_form_data, participants_full_name_list = self.process_form_meeting_data(self, data)
        if any(not x for x in [audio_file, processed_form_data, participants_full_name_list]):
            return Response({"detail": "Отсутствуют данные или файл"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            print('participants_full_name_list', participants_full_name_list)
            received_data = NeuroServerClient().send_to_neuro_server(audio_file,
                                                                     participants_full_name_list,
                                                                     processed_form_data["meeting_date"])
            processed_ai_data = self.process_ai_meeting_data(self, received_data, processed_form_data)

            serializer = MeetingSerializer(data={'audio_path': audio_file})
            if serializer.is_valid():
                meeting = serializer.save()
                meeting_id = meeting.id
            else:
                return Response({"detail": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
            processed_ai_data['meeting_id'] = meeting_id
            processed_ai_data['participants'] = processed_form_data['participants']
            return Response(processed_ai_data, status=status.HTTP_200_OK)
        except requests.RequestException as e:
            return Response({"detail": str(e)}, status=status.HTTP_502_BAD_GATEWAY)

    @staticmethod
    def process_form_meeting_data(self, data):
        data_json = json.loads(data)
        participants_list = data_json['participants']

        participants_full_name_list = []
        processed_form_data = {'meeting_date': dt.datetime.strptime(data_json['meeting_date'],
                                                                    "%Y-%m-%d").strftime("%d.%m.%Y"),
                               'participants': []}
        for emp in participants_list:
            employee = Employee.objects.get(id=emp['employee_id'])
            processed_form_data['participants'].append({'id': employee.id,
                                                'first_name': employee.first_name,
                                                'last_name': employee.last_name,
                                                'patronymic': employee.patronymic,
                                                'is_responsible': emp['is_responsible']})
            participants_full_name_list.append(
                f'{employee.last_name} {employee.first_name} {employee.patronymic or ""}'.strip()
            )

        return processed_form_data, participants_full_name_list

    @staticmethod
    def process_ai_meeting_data(self, ai_data, form_data):
        text = ai_data['report_text']
        participants_json = form_data['participants']

        parsed_data = self.parse_meeting_report(self, text, participants_json)
        parsed_data['meeting_date'] = form_data['meeting_date']
        return parsed_data

    @staticmethod
    def find_employee_id(self, full_name: str, participants: list[dict]) -> int | None:
        parts = full_name.strip().split()
        if len(parts) < 2:
            return None

        last_name = parts[0]
        first_name = parts[1]
        patronymic = parts[2] if len(parts) > 2 else None

        for p in participants:
            if (
                    p['first_name'] == first_name
                    and p['last_name'] == last_name
                    and (not patronymic or p.get('patronymic') == patronymic)
            ):
                return p['id']
        return None

    @staticmethod
    def parse_meeting_report(self, text: str, participants: list[dict]):

        # Тема совещания
        topic_match = re.search(r"\*\*Тема совещания\*\*:\s*(.*)\s*", text)
        topic = topic_match.group(1).strip() if topic_match else None

        # Ключевые вопросы
        questions_match = re.search(r"\*\*Ключевые вопросы\*\*:\s*((?:[-*].*\n)+)", text)
        questions = []
        if questions_match:
            questions_block = questions_match.group(1)
            questions = [line.strip(" -*\n") for line in questions_block.strip().splitlines()]

        # Краткое содержание
        summary_match = re.search(r"\*\*Содержание\*\*:\s*(.*?)\n+", text, re.DOTALL)
        summary = summary_match.group(1).strip() if summary_match else None

        # Задачи
        tasks = []
        task_blocks = re.split(r"\n(?=\*)", text.split("**Задачи**:")[-1].strip())
        print('participants', participants)
        print('task_blocks', task_blocks)
        for block in task_blocks:
            print('block', block)
            employee_match = re.match(r"\*(.*?)\*", block)
            print('employee_match', employee_match)
            if not employee_match:
                continue
            full_name = employee_match.group(1).strip()
            print('full_name', full_name)
            employee_id = self.find_employee_id(self, full_name, participants)
            print('employee_id', employee_id)
            if not employee_id:
                # continue или добавить в список с employee_id=None
                employee_id = None

            task_matches = re.findall(r"-\s*\*\*Задача\*\*:\s*(.*)\s*\*\*Срок\*\*:\s*(.*)", block)
            print('task_matches', task_matches)
            for content, deadline in task_matches:
                deadline = deadline.strip() if deadline.strip() else None
                print('content', content)
                print('deadline', deadline)
                tasks.append({
                    "employee_id": employee_id,
                    "content": content.strip(),
                    "deadline": deadline
                })

        return {
            "topic": topic,
            "key_questions": questions,
            "summary": summary,
            "tasks": tasks
        }
