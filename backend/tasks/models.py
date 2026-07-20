from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q


class Task(models.Model):
    content = models.TextField("Описание")
    due_date = models.DateField("Срок выполнения")
    assigned_date = models.DateField("Дата назначения", auto_now_add=True)
    employee = models.ForeignKey(
        "employees.Employee",
        verbose_name="Исполнитель",
        related_name="tasks",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    meeting = models.ForeignKey(
        "meetings.Meeting",
        verbose_name="Совещание",
        related_name="tasks",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    status = models.BooleanField("Выполнена", default=False)

    class Meta:
        verbose_name = "Задача"
        verbose_name_plural = "Задачи"
        ordering = ["status", "due_date", "id"]
        constraints = [
            models.CheckConstraint(
                condition=~Q(content=""),
                name="task_content_not_empty",
            ),
        ]
        indexes = [
            models.Index(
                fields=["employee", "status", "due_date"],
                name="task_employee_status_due_idx",
            ),
        ]

    def __str__(self) -> str:
        content = self.content.strip()
        return content if len(content) <= 50 else f"{content[:47]}..."

    def clean(self):
        super().clean()
        self.content = (self.content or "").strip()
        if not self.content:
            raise ValidationError({"content": "Описание задачи не может быть пустым."})
