from django.urls import path

from .views import (
    CustomTokenBlacklistView,
    CustomTokenObtainPairView,
    CustomTokenRefreshView,
    CustomTokenVerifyView,
)

app_name = "authentication"

urlpatterns = [
    path(
        "token/",
        CustomTokenObtainPairView.as_view(),
        name="token_obtain_pair",
    ),
    path(
        "token/refresh/",
        CustomTokenRefreshView.as_view(),
        name="token_refresh",
    ),
    path(
        "token/logout/",
        CustomTokenBlacklistView.as_view(),
        name="token_logout",
    ),
    path(
        "token/verify/",
        CustomTokenVerifyView.as_view(),
        name="token_verify",
    ),
]
