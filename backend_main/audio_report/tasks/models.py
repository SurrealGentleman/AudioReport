from django.db import models
from employees.models import Employee


class Task(models.Model):
    content = models.TextField()
    due_date = models.DateField()
    assigned_date = models.DateField(auto_now_add=True)
    employee = models.ForeignKey(Employee, on_delete=models.SET_NULL, blank=True, null=True, related_name='tasks')
    status = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.content[:20]}..."
