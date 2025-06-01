from django.core.mail import EmailMessage
from typing import List

def send_report_to_emails(subject: str, body: str, recipient_list: List[str], file_path: str):
    email = EmailMessage(
        subject=subject,
        body=body,
        from_email='alekseevalekseykla203040@gmail.com',
        to=recipient_list
    )
    email.attach_file(file_path)
    email.send()
