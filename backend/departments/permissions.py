from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsActiveSuperuserOrReadOnly(BasePermission):
    message = "Изменять отделы может только активный суперпользователь."

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True

        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.is_active
            and request.user.is_superuser
        )
