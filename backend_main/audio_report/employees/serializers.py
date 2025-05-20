from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from .models import Employee
from departments.models import Department
from posts.models import Post
from departments.serializers import DepartmentSerializer
from posts.serializers import PostSerializer


class EmployeeSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    department = DepartmentSerializer(read_only=True)
    department_id = serializers.PrimaryKeyRelatedField(
        queryset=Department.objects.all(), write_only=True, source='department'
    )
    post = PostSerializer(read_only=True)
    post_id = serializers.PrimaryKeyRelatedField(
        queryset=Post.objects.all(), write_only=True, source='post'
    )

    class Meta:
        model = Employee
        # fields = '__all__'
        exclude = ['last_login']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    @staticmethod
    def get_full_name(self, obj):
        return f"{obj.last_name} {obj.first_name} {obj.patronymic or ''}".strip()

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = Employee(**validated_data)
        user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance


class EmployeeShortSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    department = DepartmentSerializer(read_only=True)
    post = PostSerializer(read_only=True)

    class Meta:
        model = Employee
        fields = ['id', 'full_name', 'first_name', 'last_name', 'patronymic', 'department', 'post', 'email']

    @staticmethod
    def get_full_name(self, obj):
        return f"{obj.last_name} {obj.first_name} {obj.patronymic or ''}".strip()


# class LogoutSerializer(serializers.Serializer):
#     refresh = serializers.CharField()
#
#     def validate(self, attrs):
#         self.token = attrs["refresh"]
#         return attrs
#
#     def save(self, **kwargs):
#         try:
#             token = RefreshToken(self.token)
#             token.blacklist()
#         except TokenError:
#             self.fail("bad_token")