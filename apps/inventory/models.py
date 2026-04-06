from django.db import models
from django.conf import settings


class InventoryLog(models.Model):
    ACTION_CHOICES = [
        ("SET", "Set Stock"),
        ("INCREASE", "Increase Stock"),
        ("DECREASE", "Decrease Stock"),
        ("RESERVE", "Reserve Stock"),
        ("RELEASE", "Release Stock"),
        ("CONFIRM", "Confirm Deduction"),
    ]

    product_variant = models.ForeignKey(
        "products.ProductVariant",
        on_delete=models.CASCADE,
        related_name="inventory_logs"
    )

    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    quantity = models.IntegerField()

    previous_stock = models.IntegerField()
    new_stock = models.IntegerField()

    performed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    note = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["product_variant"]),
            models.Index(fields=["created_at"]),
        ]