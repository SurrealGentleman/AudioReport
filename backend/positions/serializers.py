from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from .models import Position


class PositionSerializer(serializers.ModelSerializer):
    name = serializers.CharField(
        max_length=255,
        allow_blank=False,
        trim_whitespace=True,
        validators=[
            UniqueValidator(
                queryset=Position.objects.all(),
                lookup="iexact",
                message="Должность с таким названием уже существует.",
            ),
        ],
    )

    class Meta:
        model = Position
        fields = ("id", "name")
        read_only_fields = ("id",)

    def validate_name(self, value: str) -> str:
        name = value.strip()
        if not name:
            raise serializers.ValidationError(
                "Название должности не может быть пустым."
            )
        return name
