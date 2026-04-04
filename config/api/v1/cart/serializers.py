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
        fields = ["id", "cart", "product_variant", "quantity"]
        read_only_fields = ["id"]

    def create(self, validated_data):
        cart = validated_data["cart"]
        product_variant = validated_data["product_variant"]
        quantity = validated_data.get("quantity", 1)

        item, created = CartItem.objects.get_or_create(
            cart=cart,
            product_variant=product_variant,
            defaults={
                "quantity": quantity,
                "price": product_variant.price,
            },
        )


        if not created:
            item.quantity += quantity

            # Validate stock quantity
            if item.quantity > product_variant.stock_quantity:
                raise ValidationError(
                    "Stock Quantity exceeded, please wait while we re-stock. Thank you"
                    )
            
            item.save(update_fields=["quantity"])

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