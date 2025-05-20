from django.contrib import admin
from .models import Employee


admin.site.register(Employee)  # Регистрируем модель в админке
