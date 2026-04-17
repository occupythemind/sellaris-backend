from django.db import models
from django.conf import settings
from apps.products.models import ProductVariant
from uuid import uuid4

# Unlinke the cart, the wishlist is what the user 'intends' to
# buy later on.

class Wishlist(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)

    # Authenticated user
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="wishlists",
        null=True,
        blank=True,
    )

    # Guest support
    session_id = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        db_index=True
    )

    # Optional naming (for multiple lists)
    name = models.CharField(
        max_length=255,
        blank=True,
        default=""
    )

    # Sharing capability
    is_public = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["created_at"]),
            models.Index(fields=["is_public"]),
            models.Index(fields=["user"]),
            models.Index(fields=["session_id"]),
        ]

        constraints = [
            # Must belong to either a user or a session
            models.CheckConstraint(
                condition=(
                    models.Q(user__isnull=False) |
                    models.Q(session_id__isnull=False)
                ),
                name="wishlist_user_or_session_required"
            ),

            # Optional: prevent duplicate names per user
            models.UniqueConstraint(
                fields=["name", "user", "session_id"],
                name="unique_wishlist_name_per_owner"
            )
        ]


    def __str__(self):
        return self.name or f"Wishlist {self.id}"

class WishlistItem(models.Model):
    id = models.BigAutoField(primary_key=True)

    wishlist = models.ForeignKey(
        "Wishlist",
        on_delete=models.CASCADE,
        related_name="items"
    )

    product_variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.CASCADE,
        related_name="wishlist_items"    
    )

    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            # Prevent duplicate products in same wishlist
            models.UniqueConstraint(
                fields=["wishlist", "product_variant"],
                name="unique_product_per_wishlist"
            )
        ]

    def __str__(self):
        return f"{self.product} in {self.wishlist}"