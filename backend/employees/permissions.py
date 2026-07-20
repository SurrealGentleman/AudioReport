from rest_framework.permissions import BasePermission


class IsSuperuser(BasePermission):
    message = "Операция доступна только суперпользователю."

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.is_active
            and request.user.is_superuser
        )
