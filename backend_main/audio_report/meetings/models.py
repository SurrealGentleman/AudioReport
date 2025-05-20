from django.db import models
from users.models import Employee


class Meeting(models.Model):
    topic = models.CharField(max_length=255, blank=True, null=True)
    report_path = models.FileField(upload_to='reports/', blank=True, null=True)
    report_date = models.DateField(auto_now_add=True)
    audio_path = models.FileField(upload_to='audio/')
    meeting_date = models.DateField(blank=True, null=True)

    employees = models.ManyToManyField(
        Employee,
        through='MeetingEmployee',
        related_name='meetings'
    )

    def __str__(self):
        return str(self.id)


class MeetingEmployee(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.SET_NULL, blank=True, null=True)
    meeting = models.ForeignKey(Meeting, on_delete=models.CASCADE)
    is_responsible = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.employee} - {self.meeting} (Ответственный: {self.is_responsible})"
