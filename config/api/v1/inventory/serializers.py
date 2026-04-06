from rest_framework import serializers


class StockUpdateSerializer(serializers.Serializer):
    variant_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=0)


class BulkStockUpdateSerializer(serializers.Serializer):
    updates = StockUpdateSerializer(many=True)