import json

from rest_framework import serializers

from employees.models import Employee
from meetings.validators import validate_audio_file


class GenerateParticipantSerializer(serializers.Serializer):
    employee_id = serializers.PrimaryKeyRelatedField(
        source="employee",
        queryset=Employee.objects.filter(is_active=True),
    )
    is_responsible = serializers.BooleanField(default=False)


class MeetingContextSerializer(serializers.Serializer):
    meeting_date = serializers.DateField(input_formats=("iso-8601", "%d.%m.%Y"))
    participants = GenerateParticipantSerializer(many=True, allow_empty=False)

    def validate_participants(self, participants):
        employee_ids = [item["employee"].pk for item in participants]
        if len(employee_ids) != len(set(employee_ids)):
            raise serializers.ValidationError(
                "Один сотрудник не может быть добавлен дважды."
            )
        if not any(item["is_responsible"] for item in participants):
            raise serializers.ValidationError(
                "Необходимо выбрать хотя бы одного ответственного."
            )
        return participants


class GenerateReportRequestSerializer(serializers.Serializer):
    audio = serializers.FileField()
    data = serializers.CharField(write_only=True)

    def validate_audio(self, audio):
        return validate_audio_file(audio)

    def validate_data(self, value: str):
        try:
            payload = json.loads(value)
        except (TypeError, ValueError) as error:
            raise serializers.ValidationError(
                "Поле data должно содержать корректный JSON."
            ) from error

        if not isinstance(payload, dict):
            raise serializers.ValidationError("Поле data должно содержать JSON-объект.")

        serializer = MeetingContextSerializer(data=payload)
        if not serializer.is_valid():
            raise serializers.ValidationError(serializer.errors)
        return serializer.validated_data


class GenerateReportTaskSerializer(serializers.Serializer):
    employee_id = serializers.IntegerField()
    content = serializers.CharField()
    deadline = serializers.DateField()


class GenerateReportParticipantSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    patronymic = serializers.CharField(allow_blank=True, allow_null=True)
    is_responsible = serializers.BooleanField()


class GenerateReportResponseSerializer(serializers.Serializer):
    meeting_id = serializers.IntegerField()
    meeting_date = serializers.DateField()
    topic = serializers.CharField()
    key_questions = serializers.ListField(child=serializers.CharField())
    summary = serializers.CharField()
    tasks = GenerateReportTaskSerializer(many=True)
    participants = GenerateReportParticipantSerializer(many=True)


class NeuroServerResponseSerializer(serializers.Serializer):
    report_text = serializers.CharField(allow_blank=False, trim_whitespace=True)
