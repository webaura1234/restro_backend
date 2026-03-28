from rest_framework import serializers

from .models import RestaurantConfig, Table

_RESTAURANT_CONFIG_FIELDS = (
    "id",
    "name",
    "legal_name",
    "phone",
    "email",
    "address",
    "timezone",
    "tax_rate",
    "currency",
    "updated_at",
)


class RestaurantConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = RestaurantConfig
        fields = _RESTAURANT_CONFIG_FIELDS
        read_only_fields = ("id", "updated_at")


class TableSerializer(serializers.ModelSerializer):
    """Guest/public-safe: QR material must not leak through generic list APIs."""

    class Meta:
        model = Table
        fields = (
            "id",
            "table_number",
            "seating_capacity",
            "section",
            "status",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields


class TableStaffSerializer(serializers.ModelSerializer):
    """Authenticated staff only — includes QR fields for operations."""

    class Meta:
        model = Table
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")
