from django.contrib import admin

from .models import Task


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "short_content",
        "employee",
        "meeting",
        "due_date",
        "assigned_date",
        "status",
    )
    list_filter = ("status", "due_date", "assigned_date")
    search_fields = (
        "content",
        "employee__email",
        "employee__last_name",
        "employee__first_name",
    )
    ordering = ("status", "due_date", "id")
    list_select_related = ("employee", "meeting")
    date_hierarchy = "due_date"

    @admin.display(description="Описание")
    def short_content(self, task: Task) -> str:
        return str(task)
