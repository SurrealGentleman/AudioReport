from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from .models import Department


class DepartmentSerializer(serializers.ModelSerializer):
    name = serializers.CharField(
        max_length=255,
        trim_whitespace=True,
        allow_blank=False,
        validators=(
            UniqueValidator(
                queryset=Department.objects.all(),
                lookup="iexact",
                message="Отдел с таким названием уже существует.",
            ),
        ),
    )

    class Meta:
        model = Department
        fields = (
            "id",
            "name",
        )
        read_only_fields = ("id",)

    def validate_name(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError("Название отдела не может быть пустым.")

        return value
