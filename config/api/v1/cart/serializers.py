from django.db import transaction
from django.db.models import F
from rest_framework.serializers import ModelSerializer
from rest_framework.exceptions import ValidationError

from apps.cart.models import Cart, CartItem


# Cart

class CartWriteSerializer(ModelSerializer):
    class Meta:
        model = Cart
        fields = ["id", "user", "session_id"]
        read_only_fields = ["id"]


class CartReadSerializer(ModelSerializer):
    items = lambda self, obj: CartItemReadSerializer(obj.items.all(), many=True).data
    total_price = lambda self, obj: obj.total_price

    class Meta:
        model = Cart
        fields = [
            "id",
            "user",
            "session_id",
            "items",
            "full_total_price",
            "created_at",
            "updated_at",
        ]


# Cart Item

class CartItemWriteSerializer(ModelSerializer):
    class Meta:
        model = CartItem
        fields = ["id", "product_variant", "quantity"]
        read_only_fields = ["id"]
    
    def create(self, validated_data, **kwargs):
        cart = kwargs.get("cart") or validated_data.get("cart")
        if not cart:
            raise ValidationError("Cart is required")
        variant = validated_data["product_variant"]
        qty = validated_data.get("quantity", 1)

        with transaction.atomic():
            item = (
                CartItem.objects.select_for_update()
                .filter(cart=cart, product_variant=variant)
                .first()
            )

            new_qty = (item.quantity if item else 0) + qty

            # We validate before any write
            if new_qty > variant.stock_quantity:
                raise ValidationError("Stock Quantity exceeded, please wait while we re-stock. Thank you")

            if item:
                item.quantity = F("quantity") + qty
                item.save(update_fields=["quantity"])
            else:
                item = CartItem.objects.create(
                    cart=cart,
                    product_variant=variant,
                    quantity=qty,
                    price=variant.price,
                )

        return item

    def update(self, instance, validated_data):
        new_variant = validated_data.get("product_variant", instance.product_variant)
        new_quantity = validated_data.get("quantity", instance.quantity)

        with transaction.atomic():
            # Lock the current row
            item = (
                CartItem.objects.select_for_update()
                .select_related("product_variant")
                .get(pk=instance.pk)
            )

            # If variant is changing, we must handle uniqueness
            if new_variant != item.product_variant:
                # Check if another item already exists with that variant
                existing_item = (
                    CartItem.objects.select_for_update()
                    .filter(cart=item.cart, product_variant=new_variant)
                    .exclude(pk=item.pk)
                    .first()
                )

                if existing_item:
                    # Merge quantities instead of violating unique constraint
                    combined_quantity = existing_item.quantity + new_quantity

                    if combined_quantity > new_variant.stock_quantity:
                        raise ValidationError("Stock Quantity exceeded, please wait while we re-stock. Thank you")

                    existing_item.quantity = F("quantity") + new_quantity
                    existing_item.save(update_fields=["quantity"])

                    # Delete current item since we merged
                    item.delete()
                    return existing_item

            # Validate stock
            if new_quantity > new_variant.stock_quantity:
                raise ValidationError("Stock Quantity exceeded, please wait while we re-stock. Thank you")

            # Apply updates
            item.product_variant = new_variant
            item.quantity = new_quantity
            item.price = new_variant.price  # optional: update snapshot price

            item.save()

        return item

        


class CartItemReadSerializer(ModelSerializer):
    total_price = lambda self, obj: obj.total_price

    class Meta:
        model = CartItem
        fields = [
            "id",
            "product_variant",
            "quantity",
            "price",
            "total_price",
            "created_at",
        ]