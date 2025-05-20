from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from users.serializers import EmployeeShortSerializer
from users.models import Employee


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)

        user_data = EmployeeShortSerializer(self.user).data
        data['user'] = user_data

        return data
