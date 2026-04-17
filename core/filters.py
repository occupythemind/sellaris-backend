import django_filters
from apps.inventory.models import InventoryLog


class InventoryLogFilter(django_filters.FilterSet):
    created_at__gte = django_filters.DateTimeFilter(field_name="created_at", lookup_expr="gte")
    created_at__lte = django_filters.DateTimeFilter(field_name="created_at", lookup_expr="lte")

    class Meta:
        model = InventoryLog
        fields = [
            "action",
            "product_variant",
            "performed_by",
        ]