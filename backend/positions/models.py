from django.db import models
from django.db.models.functions import Lower


class Position(models.Model):
    name = models.CharField("Название", max_length=255, unique=True)

    class Meta:
        verbose_name = "Должность"
        verbose_name_plural = "Должности"
        ordering = ["name", "id"]
        constraints = [
            models.UniqueConstraint(
                Lower("name"),
                name="position_name_case_insensitive_unique",
            ),
        ]

    def __str__(self) -> str:
        return self.name

    def clean(self):
        super().clean()
        self.name = (self.name or "").strip()
