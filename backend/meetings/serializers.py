from rest_framework import serializers

from employees.models import Employee
from employees.serializers import EmployeeShortSerializer

from .models import Meeting, MeetingEmployee
from .validators import validate_audio_file


class MeetingUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Meeting
        fields = ("id", "audio_path")
        read_only_fields = ("id",)

    def validate_audio_path(self, audio):
        return validate_audio_file(audio)


class MeetingParticipantSerializer(serializers.ModelSerializer):
    employee = EmployeeShortSerializer(read_only=True)

    class Meta:
        model = MeetingEmployee
        fields = ("employee", "is_responsible")
        read_only_fields = fields


class MeetingReadSerializer(serializers.ModelSerializer):
    participants = MeetingParticipantSerializer(
        source="memberships",
        many=True,
        read_only=True,
    )

    class Meta:
        model = Meeting
        fields = (
            "id",
            "topic",
            "meeting_date",
            "report_path",
            "report_date",
            "audio_path",
            "participants",
        )
        read_only_fields = fields


class TaskInputSerializer(serializers.Serializer):
    employee_id = serializers.PrimaryKeyRelatedField(
        source="employee",
        queryset=Employee.objects.filter(is_active=True),
    )
    content = serializers.CharField(max_length=5000, trim_whitespace=True)
    deadline = serializers.DateField(input_formats=("%d.%m.%Y", "iso-8601"))


class ParticipantInputSerializer(serializers.Serializer):
    id = serializers.PrimaryKeyRelatedField(
        source="employee",
        queryset=Employee.objects.filter(is_active=True),
    )
    is_responsible = serializers.BooleanField(default=False)


class ReportInputSerializer(serializers.Serializer):
    topic = serializers.CharField(max_length=255, trim_whitespace=True)
    key_questions = serializers.ListField(
        child=serializers.CharField(max_length=2000, trim_whitespace=True),
        allow_empty=True,
    )
    summary = serializers.CharField(max_length=20_000, trim_whitespace=True)
    tasks = TaskInputSerializer(many=True, allow_empty=True)
    meeting_date = serializers.DateField(
        input_formats=("%d.%m.%Y", "iso-8601"),
    )
    meeting_id = serializers.PrimaryKeyRelatedField(
        source="meeting",
        queryset=Meeting.objects.all(),
    )
    participants = ParticipantInputSerializer(many=True, allow_empty=False)

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

    def validate(self, attrs):
        participant_ids = {item["employee"].pk for item in attrs["participants"]}
        invalid_task_employees = {
            item["employee"].pk
            for item in attrs["tasks"]
            if item["employee"].pk not in participant_ids
        }
        if invalid_task_employees:
            raise serializers.ValidationError(
                {"tasks": ("Задачи можно назначать только участникам совещания.")}
            )
        return attrs
