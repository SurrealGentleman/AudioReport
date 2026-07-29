from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from employees.serializers import AuthenticatedEmployeeSerializer


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        data["user"] = AuthenticatedEmployeeSerializer(
            self.user,
            context=self.context,
        ).data
        return data
