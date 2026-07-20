from meetings.serializers import MeetingUploadSerializer

from .neuro_client import AIInvalidResponseError, NeuroServerClient
from .parsers import parse_ai_report
from .serializers import NeuroServerResponseSerializer


def _participant_payload(participant: dict) -> dict:
    employee = participant["employee"]
    return {
        "id": employee.pk,
        "first_name": employee.first_name,
        "last_name": employee.last_name,
        "patronymic": employee.patronymic,
        "is_responsible": participant["is_responsible"],
    }


def generate_meeting_report(
    audio_file,
    meeting_data: dict,
    creator,
    client=None,
) -> dict:
    participants = [
        _participant_payload(participant)
        for participant in meeting_data["participants"]
    ]
    participant_names = [
        " ".join(
            part
            for part in (
                participant["last_name"],
                participant["first_name"],
                participant["patronymic"],
            )
            if part
        )
        for participant in participants
    ]

    client = client or NeuroServerClient()
    response_payload = client.generate_report(
        audio_file=audio_file,
        participants=participant_names,
        meeting_date=meeting_data["meeting_date"].strftime("%d.%m.%Y"),
    )

    response_serializer = NeuroServerResponseSerializer(data=response_payload)
    if not response_serializer.is_valid():
        raise AIInvalidResponseError(
            "AI service response does not contain report_text."
        )

    report = parse_ai_report(
        response_serializer.validated_data["report_text"],
        participants,
    )

    audio_file.seek(0)
    meeting_serializer = MeetingUploadSerializer(
        data={"audio_path": audio_file},
    )
    meeting_serializer.is_valid(raise_exception=True)
    meeting = meeting_serializer.save(created_by=creator)

    report.update(
        {
            "meeting_id": meeting.pk,
            "meeting_date": meeting_data["meeting_date"].strftime("%d.%m.%Y"),
            "participants": participants,
        }
    )
    return report
