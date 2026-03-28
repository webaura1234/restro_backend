from rest_framework import serializers

from .models import DailyAnalytics, ItemAnalytics


class DailyAnalyticsSerializer(serializers.ModelSerializer):
    class Meta:
        model = DailyAnalytics
        fields = "__all__"
        read_only_fields = ("id", "created_at")


class ItemAnalyticsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemAnalytics
        fields = "__all__"
        read_only_fields = ("id", "created_at")
