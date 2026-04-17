from rest_framework import serializers
from apps.payments.models import Payment


class PaymentRecordReadSerializer(serializers.ModelSerializer):
    order_id = serializers.UUIDField(source="order.id", read_only=True)

    class Meta:
        model = Payment
        fields = [
            "id",
            "order_id",
            "amount",
            "currency",
            "status",
            "provider",
            "reference_id",
            "transaction_id",
            "payment_link",
            "created_at",
            "confirmed_at",
        ]