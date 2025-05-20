from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from employees.serializers import EmployeeShortSerializer
from employees.models import Employee


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)

        user_data = EmployeeShortSerializer(self.user).data
        data['user'] = user_data

        return data
