import datetime
import os
from rest_framework import serializers
from .models import Meeting
from employees.serializers import EmployeeShortSerializer
from employees.models import Employee


# первое создание записи
class MeetingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Meeting
        fields = ['id', 'audio_path']
        read_only_fields = ['id']

    def create(self, validated_data):
        audio = validated_data.get('audio_path')
        if audio:
            now_str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            ext = os.path.splitext(audio.name)[1]  # расширение
            audio.name = f"audio_{now_str}{ext}"
        return super().create(validated_data)


# отображение записей
class ReportSerializer(serializers.ModelSerializer):
    # employees = MeetingEmployeeSerializer(many=True, source='meetingemployee_set', read_only=False)
    meeting_date = serializers.DateField(input_formats=["%Y-%m-%d"])

    class Meta:
        model = Meeting
        fields = ["id", "meeting_date", "topic", "report_path", "report_date", "audio_path"]
        # fields = '__all__'


# вспомогательные
class TaskInputSerializer(serializers.Serializer):
    employee_id = serializers.IntegerField()
    content = serializers.CharField()
    deadline = serializers.CharField()


class ParticipantInputSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    patronymic = serializers.CharField(allow_null=True, required=False)
    is_responsible = serializers.BooleanField()


class ReportInputSerializer(serializers.Serializer):
    topic = serializers.CharField()
    key_questions = serializers.ListField(child=serializers.CharField())
    summary = serializers.CharField()
    tasks = TaskInputSerializer(many=True)
    meeting_date = serializers.DateField(input_formats=["%d.%m.%Y"])
    meeting_id = serializers.IntegerField()
    participants = ParticipantInputSerializer(many=True)
