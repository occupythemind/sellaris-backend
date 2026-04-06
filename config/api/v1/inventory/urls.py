from django.urls import path
from .views import (
    SetStockAPIView,
    AdjustStockAPIView,
    BulkStockUpdateAPIView,
    InventoryLogAPIView,
)

urlpatterns = [
    path('set-stock-quantity/', SetStockAPIView.as_view(), name='set-stock'),
    path('adjust-stock-quantity/', AdjustStockAPIView.as_view(), name='adjust-stock'),
    path('bulk-stock-quantity-update/', BulkStockUpdateAPIView.as_view(), name='bulk-stock-update'),
    path('inventory-log/', InventoryLogAPIView.as_view(), name='inventory-log'),
]