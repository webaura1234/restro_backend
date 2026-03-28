from rest_framework import serializers

from .models import TableSession


class TableSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TableSession
        fields = "__all__"
        read_only_fields = ("id", "opened_at")
