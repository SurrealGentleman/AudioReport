from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from departments.models import Department
from departments.serializers import DepartmentSerializer
from positions.models import Position
from positions.serializers import PositionSerializer

from .models import Employee


class EmployeeReadSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(
        source="get_full_name",
        read_only=True,
    )
    department = DepartmentSerializer(
        read_only=True,
    )
    position = PositionSerializer(
        read_only=True,
    )

    class Meta:
        model = Employee
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "patronymic",
            "full_name",
            "department",
            "position",
            "is_active",
            "is_staff",
            "is_superuser",
            "date_joined",
            "last_login",
        ]
        read_only_fields = fields


class EmployeeCreateSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        validators=[
            UniqueValidator(
                queryset=Employee.objects.all(),
                lookup="iexact",
                message="Сотрудник с таким email уже существует.",
            ),
        ],
    )
    password = serializers.CharField(
        write_only=True,
        trim_whitespace=False,
        style={"input_type": "password"},
    )
    department_id = serializers.PrimaryKeyRelatedField(
        source="department",
        queryset=Department.objects.all(),
        write_only=True,
        required=True,
        allow_null=False,
    )
    position_id = serializers.PrimaryKeyRelatedField(
        source="position",
        queryset=Position.objects.all(),
        write_only=True,
        required=True,
        allow_null=False,
    )

    class Meta:
        model = Employee
        fields = [
            "email",
            "password",
            "first_name",
            "last_name",
            "patronymic",
            "department_id",
            "position_id",
        ]

    def validate_email(self, value):
        return Employee.objects.normalize_employee_email(value)

    def validate(self, attrs):
        attrs = super().validate(attrs)

        password = attrs.get("password")

        candidate = Employee(
            email=attrs.get("email", ""),
            first_name=attrs.get("first_name", ""),
            last_name=attrs.get("last_name", ""),
            patronymic=attrs.get("patronymic", ""),
            department=attrs.get("department"),
            position=attrs.get("position"),
        )

        try:
            validate_password(
                password=password,
                user=candidate,
            )
        except DjangoValidationError as error:
            raise serializers.ValidationError(
                {"password": list(error.messages)}
            ) from error

        return attrs

    def create(self, validated_data):
        password = validated_data.pop("password")

        return Employee.objects.create_user(
            password=password,
            **validated_data,
        )


class EmployeeUpdateSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=False,
        validators=[
            UniqueValidator(
                queryset=Employee.objects.all(),
                lookup="iexact",
                message="Сотрудник с таким email уже существует.",
            ),
        ],
    )
    department_id = serializers.PrimaryKeyRelatedField(
        source="department",
        queryset=Department.objects.all(),
        write_only=True,
        required=False,
        allow_null=False,
    )
    position_id = serializers.PrimaryKeyRelatedField(
        source="position",
        queryset=Position.objects.all(),
        write_only=True,
        required=False,
        allow_null=False,
    )

    class Meta:
        model = Employee
        fields = [
            "email",
            "first_name",
            "last_name",
            "patronymic",
            "department_id",
            "position_id",
        ]
        extra_kwargs = {
            "first_name": {
                "required": False,
                "allow_blank": False,
            },
            "last_name": {
                "required": False,
                "allow_blank": False,
            },
            "patronymic": {
                "required": False,
                "allow_blank": True,
            },
        }

    def validate_email(self, value):
        return Employee.objects.normalize_employee_email(value)

    def update(self, instance, validated_data):
        for attribute, value in validated_data.items():
            setattr(instance, attribute, value)

        instance.full_clean()
        instance.save()

        return instance


class EmployeePasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(
        write_only=True,
        trim_whitespace=False,
        style={"input_type": "password"},
    )

    def validate_new_password(self, value):
        employee = self.instance

        if employee is None:
            raise serializers.ValidationError("Сотрудник не указан.")

        try:
            validate_password(
                password=value,
                user=employee,
            )
        except DjangoValidationError as error:
            raise serializers.ValidationError(list(error.messages)) from error

        return value

    def save(self, **kwargs):
        employee = self.instance
        employee.set_password(self.validated_data["new_password"])
        employee.save(update_fields=["password"])

        return employee


class EmployeeSelfPasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(
        write_only=True,
        trim_whitespace=False,
    )
    new_password = serializers.CharField(
        write_only=True,
        trim_whitespace=False,
    )

    def validate_current_password(self, value):
        employee = self.instance

        if not employee.check_password(value):
            raise serializers.ValidationError("Текущий пароль указан неверно.")

        return value

    def validate_new_password(self, value):
        try:
            validate_password(
                password=value,
                user=self.instance,
            )
        except DjangoValidationError as error:
            raise serializers.ValidationError(list(error.messages)) from error

        return value

    def save(self, **kwargs):
        employee = self.instance
        employee.set_password(self.validated_data["new_password"])
        employee.save(update_fields=["password"])

        return employee


class EmployeeAccessSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = [
            "is_active",
            "is_staff",
        ]

    def validate(self, attrs):
        attrs = super().validate(attrs)

        request = self.context.get("request")
        employee = self.instance

        if request and employee == request.user:
            if attrs.get("is_active") is False:
                raise serializers.ValidationError(
                    {
                        "is_active": "Нельзя деактивировать собственную учётную запись.",
                    }
                )

            if attrs.get("is_staff") is False:
                raise serializers.ValidationError(
                    {
                        "is_staff": (
                            "Нельзя отозвать собственный административный доступ."
                        ),
                    }
                )

        return attrs


class EmployeeShortSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(
        source="get_full_name",
        read_only=True,
    )
    department = DepartmentSerializer(
        read_only=True,
    )
    position = PositionSerializer(
        read_only=True,
    )

    class Meta:
        model = Employee
        fields = [
            "id",
            "full_name",
            "first_name",
            "last_name",
            "patronymic",
            "department",
            "position",
        ]
        read_only_fields = fields


class AuthenticatedEmployeeSerializer(EmployeeShortSerializer):
    class Meta(EmployeeShortSerializer.Meta):
        fields = [
            *EmployeeShortSerializer.Meta.fields,
            "email",
            "is_active",
            "is_staff",
            "is_superuser",
        ]
        read_only_fields = fields
