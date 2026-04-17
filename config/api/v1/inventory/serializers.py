from rest_framework import serializers
from apps.inventory.models import InventoryLog


class StockQuantityUpdateSerializer(serializers.Serializer):
    variant_id = serializers.UUIDField()
    quantity = serializers.IntegerField(min_value=0)


class AdjustStockQuantitySerializer(serializers.Serializer):
    variant_id = serializers.UUIDField()
    quantity = serializers.IntegerField(min_value=0)

    ACTION_CHOICES = [
        ("INCREASE", "INCREASE"),
        ("DECREASE", "DECREASE")
    ]

    action = serializers.ChoiceField(choices=ACTION_CHOICES)


class BulkStockQuantityUpdateSerializer(serializers.Serializer):
    updates = StockQuantityUpdateSerializer(many=True)


class InventoryLogReadSerializer(serializers.Serializer):
    logs = serializers.CharField(max_length=200)