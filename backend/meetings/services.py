import logging
from collections import defaultdict
from pathlib import Path

from django.conf import settings
from django.db import transaction
from django.utils import timezone

from tasks.models import Task

from .models import Meeting, MeetingEmployee
from .render_docx import render_docx_template
from .send_email import send_report_to_emails

logger = logging.getLogger(__name__)


def _employee_full_name(employee) -> str:
    return employee.get_full_name() or employee.email


def build_report_context(validated_data: dict) -> dict:
    tasks_by_employee = defaultdict(list)
    for task in validated_data["tasks"]:
        tasks_by_employee[task["employee"].pk].append(task)

    task_blocks = []
    for number, participant in enumerate(validated_data["participants"], 1):
        employee = participant["employee"]
        employee_tasks = tasks_by_employee.get(employee.pk, [])
        if not employee_tasks:
            continue

        lines = [f"{number}. {_employee_full_name(employee)}"]
        lines.extend(
            f"    – {task['content']} / {task['deadline'].strftime('%d.%m.%Y')}"
            for task in employee_tasks
        )
        task_blocks.append("\n".join(lines))

    participants = validated_data["participants"]
    responsible_names = [
        _employee_full_name(item["employee"])
        for item in participants
        if item["is_responsible"]
    ]

    return {
        "topic": validated_data["topic"],
        "meeting_date": validated_data["meeting_date"].strftime("%d.%m.%Y"),
        "summary": validated_data["summary"],
        "key_questions": "\n".join(
            f"– {question}" for question in validated_data["key_questions"]
        ),
        "participants": ", ".join(
            _employee_full_name(item["employee"]) for item in participants
        ),
        "tasks": "\n\n".join(task_blocks),
        "responsible": ", ".join(responsible_names),
        "now_date": timezone.localdate().strftime("%d.%m.%Y"),
    }


def _send_report_email(report_path: Path, recipients: list[str]) -> None:
    try:
        send_report_to_emails(
            subject="Отчёт по совещанию",
            body=("Здравствуйте! Во вложении — отчёт по итогам совещания."),
            recipient_list=recipients,
            file_path=report_path,
        )
    except Exception:
        logger.exception("Не удалось отправить отчёт участникам совещания.")


def _delete_local_media_file(file_path: Path | None) -> None:
    if file_path is None:
        return

    media_root = Path(settings.MEDIA_ROOT).resolve()
    resolved_path = file_path.resolve()
    if resolved_path.is_relative_to(media_root):
        resolved_path.unlink(missing_ok=True)
    else:
        logger.warning("Refused to delete a file outside MEDIA_ROOT.")


def save_meeting_report(validated_data: dict) -> Meeting:
    meeting = validated_data["meeting"]
    context = build_report_context(validated_data)
    previous_report_path = (
        Path(settings.MEDIA_ROOT) / meeting.report_path.name
        if meeting.report_path.name
        else None
    )

    reports_dir = Path(settings.MEDIA_ROOT) / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    timestamp = timezone.now().strftime("%Y%m%d_%H%M%S_%f")
    filename = f"report_{meeting.pk}_{timestamp}.docx"
    output_path = reports_dir / filename

    render_docx_template(
        Path(settings.MEDIA_ROOT) / "templates" / "meeting_template.docx",
        context,
        output_path,
    )

    participants = validated_data["participants"]
    tasks = validated_data["tasks"]

    try:
        with transaction.atomic():
            meeting.topic = validated_data["topic"]
            meeting.meeting_date = validated_data["meeting_date"]
            meeting.report_path.name = f"reports/{filename}"
            meeting.save(
                update_fields=("topic", "meeting_date", "report_path"),
            )

            meeting.memberships.all().delete()
            MeetingEmployee.objects.bulk_create(
                MeetingEmployee(
                    meeting=meeting,
                    employee=item["employee"],
                    is_responsible=item["is_responsible"],
                )
                for item in participants
            )

            meeting.tasks.all().delete()
            Task.objects.bulk_create(
                Task(
                    meeting=meeting,
                    employee=item["employee"],
                    content=item["content"],
                    due_date=item["deadline"],
                )
                for item in tasks
            )

            recipients = list(
                dict.fromkeys(
                    item["employee"].email
                    for item in participants
                    if item["employee"].email
                )
            )
            transaction.on_commit(
                lambda: _send_report_email(output_path, recipients),
            )
            if previous_report_path != output_path:
                transaction.on_commit(
                    lambda: _delete_local_media_file(previous_report_path),
                )
    except Exception:
        _delete_local_media_file(output_path)
        raise

    return meeting
