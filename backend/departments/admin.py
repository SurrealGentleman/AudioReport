from django.contrib import admin

from .models import Department


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
    )
    list_display_links = (
        "id",
        "name",
    )
    search_fields = ("name",)
    ordering = ("name", "id")
