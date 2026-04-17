from django.db import transaction
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from rest_framework import status

from core.permissions import IsStaffUser
from apps.inventory.services import set_stock, adjust_stock
from apps.inventory.models import InventoryLog
from core.filters import InventoryLogFilter
from core.pagination import LogPagination
from .serializers import (
    StockQuantityUpdateSerializer, 
    AdjustStockQuantitySerializer,
    BulkStockQuantityUpdateSerializer,
    InventoryLogReadSerializer,
)


class SetStockAPIView(APIView):
    """
    Set the stock quantity for a single product variant
    """
    permission_classes = [IsStaffUser]

    def post(self, request):
        serializer = StockQuantityUpdateSerializer(data=request.data)
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
        serializer = AdjustStockQuantitySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        variant_id = serializer.validated_data["variant_id"]
        quantity = serializer.validated_data["quantity"]
        action = serializer.validated_data["action"]  # INCREASE / DECREASE

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
    permission_classes = [IsStaffUser]

    @transaction.atomic
    def post(self, request):
        serializer = BulkStockQuantityUpdateSerializer(data=request.data)
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
    Supports filtering, search, ordering, pagination
    """
    permission_classes = [IsAdminUser]
    serializer_class = InventoryLogReadSerializer

    queryset = InventoryLog.objects.select_related(
        "product_variant",
        "performed_by"
    ).all()

    filter_backends = [
        DjangoFilterBackend,
        SearchFilter,
        OrderingFilter,
    ]

    filterset_fields = [
        "action",
        "product_variant",
        "performed_by",
    ]

    filterset_class = InventoryLogFilter
    pagination_class = LogPagination

    search_fields = [
        "note",
        "product_variant__name",
        "performed_by__email",
    ]

    ordering_fields = [
        "created_at",
        "quantity",
        "new_stock",
        "previous_stock",
    ]

    ordering = ["-created_at"]