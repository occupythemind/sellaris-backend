from django.db import models
from django.conf import settings
from django.apps import apps
from core.utils import get_price_decimal_field
from decimal import Decimal
from uuid import uuid4


class Cart(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)

    # For logged-in users
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="carts",
        null=True,
        blank=True,
    )

    # For guest users (session-based)
    session_id = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        db_index=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=(
                    models.Q(user__isnull=False) | models.Q(session_id__isnull=False)
                ),
                name="cart_user_or_session_required"
            ),

            # Prevent multiple active carts per user:
            models.UniqueConstraint(
                fields=["user"],
                condition=models.Q(user__isnull=False),
                name="unique_active_cart_per_user"
            ),
        ]

    def __str__(self):
        return f"Cart {self.id}"
    
class CartItem(models.Model):
    id = models.BigAutoField(primary_key=True)

    cart = models.ForeignKey(
        "Cart",
        on_delete=models.CASCADE,
        related_name="items"
    )

    product_variant = models.ForeignKey(
        apps.get_model("products", "ProductVariant"),
        on_delete=models.CASCADE,
        related_name="cart_items"
    )

    quantity = models.PositiveIntegerField(default=1)

    # Snapshot price at time of adding to cart
    price = get_price_decimal_field()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            # Prevent duplicate variant in same cart
            models.UniqueConstraint(
                fields=["cart", "product_variant"],
                name="unique_product_per_cart"
            )
        ]

    def __str__(self):
        return f"{self.product_variant} x {self.quantity}"

    @property
    def total_price(self) -> Decimal:
        return self.quantity * self.price