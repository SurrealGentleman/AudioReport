from django.contrib import admin
from .models import Meeting, MeetingEmployee


admin.site.register(Meeting)  # Регистрируем модель в админке
admin.site.register(MeetingEmployee)  # Регистрируем модель в админке
