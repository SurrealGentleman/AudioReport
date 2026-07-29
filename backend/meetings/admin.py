from django.contrib import admin

from .models import Meeting, MeetingEmployee


class MeetingEmployeeInline(admin.TabularInline):
    model = MeetingEmployee
    extra = 0
    autocomplete_fields = ("employee",)


@admin.register(Meeting)
class MeetingAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "topic",
        "meeting_date",
        "report_date",
        "created_by",
        "has_report",
    )
    list_filter = ("meeting_date", "report_date")
    search_fields = (
        "topic",
        "created_by__email",
        "memberships__employee__email",
        "memberships__employee__last_name",
    )
    ordering = ("-meeting_date", "-id")
    list_select_related = ("created_by",)
    autocomplete_fields = ("created_by",)
    readonly_fields = ("report_date",)
    inlines = (MeetingEmployeeInline,)

    @admin.display(boolean=True, description="Отчёт сформирован")
    def has_report(self, meeting: Meeting) -> bool:
        return bool(meeting.report_path)


@admin.register(MeetingEmployee)
class MeetingEmployeeAdmin(admin.ModelAdmin):
    list_display = ("id", "meeting", "employee", "is_responsible")
    list_filter = ("is_responsible",)
    search_fields = (
        "meeting__topic",
        "employee__email",
        "employee__last_name",
    )
    list_select_related = ("meeting", "employee")
    autocomplete_fields = ("meeting", "employee")
