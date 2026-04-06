from django.db import transaction
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from rest_framework import status

from core.permissions import IsStaffUser
from apps.inventory.services import set_stock, adjust_stock
from apps.inventory.models import InventoryLog
from .serializers import StockUpdateSerializer, BulkStockUpdateSerializer



class SetStockAPIView(APIView):
    """
    Set the stock quantity for a single product variant
    """
    permission_classes = [IsStaffUser]

    def post(self, request):
        serializer = StockUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        set_stock(
            variant_id=serializer.validated_data["variant_id"],
            quantity=serializer.validated_data["quantity"],
            user=request.user
        )

        return Response({"detail": "Stock quantity updated"})
    

class AdjustStockAPIView(APIView):
    """
    Adjust (either increase or decrease) the stock quantity for a 
    single product variant
    """
    permission_classes = [IsStaffUser]

    def post(self, request):
        variant_id = request.data.get("variant_id")
        quantity = int(request.data.get("quantity"))
        action = request.data.get("action")  # INCREASE / DECREASE

        adjust_stock(
            variant_id=variant_id,
            quantity=quantity,
            action=action,
            user=request.user
        )

        return Response({"detail": "Stock quantity adjusted"})
    

class BulkStockUpdateAPIView(APIView):
    """
    Update the stock quantity of more than one product variant
    """
    permission_classes = [IsAdminUser]

    @transaction.atomic
    def post(self, request):
        serializer = BulkStockUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        for item in serializer.validated_data["updates"]:
            set_stock(
                variant_id=item["variant_id"],
                quantity=item["quantity"],
                user=request.user
            )

        return Response({"detail": "Bulk stock quantity update successful"})
    

class InventoryLogAPIView(ListAPIView):
    """
    Audit the InventoryLogs (READ-ONLY)
    """
    permission_classes = [IsAdminUser]
    queryset = InventoryLog.objects.all().order_by("-created_at")