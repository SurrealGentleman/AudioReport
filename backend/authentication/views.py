from rest_framework.throttling import ScopedRateThrottle
from rest_framework_simplejwt.views import (
    TokenBlacklistView,
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

from .serializers import CustomTokenObtainPairSerializer


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
    throttle_classes = (ScopedRateThrottle,)
    throttle_scope = "auth_login"


class CustomTokenRefreshView(TokenRefreshView):
    throttle_classes = (ScopedRateThrottle,)
    throttle_scope = "auth_refresh"


class CustomTokenBlacklistView(TokenBlacklistView):
    throttle_classes = (ScopedRateThrottle,)
    throttle_scope = "auth_logout"


class CustomTokenVerifyView(TokenVerifyView):
    throttle_classes = (ScopedRateThrottle,)
    throttle_scope = "auth_verify"
