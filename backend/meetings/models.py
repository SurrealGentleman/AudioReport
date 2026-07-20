from pathlib import Path
from uuid import uuid4

from django.conf import settings
from django.db import models
from django.db.models import Q


def meeting_audio_upload_to(instance, filename: str) -> str:
    extension = Path(filename).suffix.lower()
    return f"audio/{uuid4().hex}{extension}"


class Meeting(models.Model):
    topic = models.CharField("Тема", max_length=255, blank=True, default="")
    report_path = models.FileField(
        "Отчёт",
        upload_to="reports/",
        blank=True,
    )
    report_date = models.DateField("Дата создания", auto_now_add=True)
    audio_path = models.FileField(
        "Аудиозапись",
        upload_to=meeting_audio_upload_to,
    )
    meeting_date = models.DateField("Дата совещания", blank=True, null=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="Создатель",
        related_name="created_meetings",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    employees = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        verbose_name="Участники",
        through="MeetingEmployee",
        related_name="meetings",
    )

    class Meta:
        verbose_name = "Совещание"
        verbose_name_plural = "Совещания"
        ordering = ["-meeting_date", "-id"]
        indexes = [
            models.Index(
                fields=["meeting_date"],
                name="meeting_date_idx",
            ),
        ]

    def __str__(self) -> str:
        return self.topic or f"Совещание №{self.pk or '—'}"


class MeetingEmployee(models.Model):
    employee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="Сотрудник",
        related_name="meeting_memberships",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    meeting = models.ForeignKey(
        Meeting,
        verbose_name="Совещание",
        related_name="memberships",
        on_delete=models.CASCADE,
    )
    is_responsible = models.BooleanField("Ответственный", default=False)

    class Meta:
        verbose_name = "Участник совещания"
        verbose_name_plural = "Участники совещаний"
        ordering = ["meeting_id", "employee_id", "id"]
        constraints = [
            models.UniqueConstraint(
                fields=["meeting", "employee"],
                condition=Q(employee__isnull=False),
                name="meeting_employee_unique_membership",
            ),
        ]

    def __str__(self) -> str:
        employee = str(self.employee) if self.employee else "Удалённый сотрудник"
        return f"{employee} — {self.meeting}"
