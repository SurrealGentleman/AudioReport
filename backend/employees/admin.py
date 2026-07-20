from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .forms import EmployeeChangeForm, EmployeeCreationForm
from .models import Employee


@admin.register(Employee)
class EmployeeAdmin(BaseUserAdmin):
    form = EmployeeChangeForm
    add_form = EmployeeCreationForm

    list_display = [
        "email",
        "display_full_name",
        "department",
        "position",
        "is_active",
        "is_staff",
        "is_superuser",
        "date_joined",
    ]
    list_display_links = [
        "email",
        "display_full_name",
    ]
    list_filter = [
        "is_active",
        "is_staff",
        "is_superuser",
        "department",
        "position",
    ]
    search_fields = [
        "email",
        "first_name",
        "last_name",
        "patronymic",
    ]
    ordering = [
        "last_name",
        "first_name",
        "id",
    ]
    list_select_related = [
        "department",
        "position",
    ]

    readonly_fields = [
        "last_login",
        "date_joined",
    ]

    filter_horizontal = [
        "groups",
        "user_permissions",
    ]

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "email",
                    "password",
                ),
            },
        ),
        (
            "Персональные данные",
            {
                "fields": (
                    "last_name",
                    "first_name",
                    "patronymic",
                ),
            },
        ),
        (
            "Работа",
            {
                "fields": (
                    "department",
                    "position",
                ),
            },
        ),
        (
            "Статус",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                ),
            },
        ),
        (
            "Права доступа",
            {
                "fields": (
                    "groups",
                    "user_permissions",
                ),
                "classes": ("collapse",),
            },
        ),
        (
            "Важные даты",
            {
                "fields": (
                    "last_login",
                    "date_joined",
                ),
            },
        ),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "last_name",
                    "first_name",
                    "patronymic",
                    "department",
                    "position",
                    "password1",
                    "password2",
                    "is_active",
                    "is_staff",
                    "is_superuser",
                ),
            },
        ),
    )

    actions = [
        "activate_employees",
        "deactivate_employees",
    ]

    @admin.display(
        description="ФИО",
        ordering="last_name",
    )
    def display_full_name(self, employee):
        return employee.get_full_name()

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = list(super().get_readonly_fields(request, obj))

        readonly_fields.extend(
            [
                "last_login",
                "date_joined",
            ]
        )

        if not request.user.is_superuser:
            readonly_fields.extend(
                [
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ]
            )

        return list(dict.fromkeys(readonly_fields))

    def has_change_permission(
        self,
        request,
        obj=None,
    ):
        has_permission = super().has_change_permission(
            request,
            obj,
        )

        if not has_permission:
            return False

        return not (
            obj is not None and obj.is_superuser and not request.user.is_superuser
        )

    def has_delete_permission(
        self,
        request,
        obj=None,
    ):
        has_permission = super().has_delete_permission(
            request,
            obj,
        )

        if not has_permission:
            return False

        protected_superuser = (
            obj is not None and obj.is_superuser and not request.user.is_superuser
        )
        deleting_self = obj is not None and obj == request.user

        return not (protected_superuser or deleting_self)

    def get_actions(self, request):
        actions = super().get_actions(request)

        if not request.user.is_superuser:
            actions.pop("activate_employees", None)
            actions.pop("deactivate_employees", None)

        return actions

    @admin.action(description="Деактивировать выбранных сотрудников")
    def deactivate_employees(self, request, queryset):
        queryset.exclude(
            pk=request.user.pk,
        ).filter(
            is_superuser=False,
        ).update(
            is_active=False,
        )

    @admin.action(description="Активировать выбранных сотрудников")
    def activate_employees(self, request, queryset):
        queryset.update(
            is_active=True,
        )
