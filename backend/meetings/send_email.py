from collections.abc import Sequence
from pathlib import Path

from django.conf import settings
from django.core.mail import EmailMessage


def send_report_to_emails(
    subject: str,
    body: str,
    recipient_list: Sequence[str],
    file_path: Path,
) -> int:
    recipients = list(dict.fromkeys(recipient_list))
    if not recipients:
        return 0
    if not file_path.is_file():
        raise FileNotFoundError(f"Файл отчёта не найден: {file_path}")

    email = EmailMessage(
        subject=subject,
        body=body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=recipients,
    )
    email.attach_file(file_path)
    return email.send(fail_silently=False)
