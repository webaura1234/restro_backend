from rest_framework import serializers

from .models import Bill, Payment


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class BillSerializer(serializers.ModelSerializer):
    payments = PaymentSerializer(many=True, read_only=True)

    class Meta:
        model = Bill
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")
