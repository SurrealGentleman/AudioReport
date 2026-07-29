from django.db import models
from django.db.models.functions import Lower


class Department(models.Model):
    name = models.CharField(
        "Название",
        max_length=255,
        unique=True,
    )

    class Meta:
        verbose_name = "Отдел"
        verbose_name_plural = "Отделы"
        ordering = ["name", "id"]
        constraints = [
            models.UniqueConstraint(
                Lower("name"),
                name="department_name_case_insensitive_unique",
            ),
        ]

    def __str__(self) -> str:
        return self.name

    def clean(self):
        super().clean()
        self.name = (self.name or "").strip()
