from django.db import transaction
from rest_framework.serializers import ModelSerializer, ValidationError
from apps.orders.models import Order, OrderItem


# Order Item

class OrderItemReadSerializer(ModelSerializer):
    class Meta:
        model = OrderItem
        fields = [
            "id",
            "product_variant",
            "product_name",
            "price",
            "quantity",
            "total_price",
        ]


# Order

class OrderWriteSerializer(ModelSerializer):
    class Meta:
        model = Order
        fields = ["id", "email", "phone_number"]
        read_only_fields = ["id"]

    @transaction.atomic
    def create(self, validated_data):
        request = self.context["request"]

        user = request.user if request.user.is_authenticated else None
        session_id = request.session.session_key

        cart = self._get_cart(user, session_id)

        if not cart or not cart.items.exists():
            raise ValidationError("Cart is empty")

        # PRICE VALIDATION
        price_changes = []

        for item in cart.items.select_related("product_variant"):
            current_price = item.product_variant.price

            if item.price != current_price:
                price_changes.append({
                    "product": str(item.product_variant),
                    "old_price": item.price,
                    "new_price": current_price
                })

                # AUTO-UPDATE CART
                item.price = current_price
                item.total_price = current_price * item.quantity
                item.save(update_fields=["price", "total_price"])

        if price_changes:
            raise ValidationError({
                "error": "PRICE_CHANGED",
                "message": "Some item prices have changed. Your cart has been updated.",
                "changes": price_changes
            })

        # SAFE TO CREATE ORDER NOW
        total_amount = sum(item.total_price for item in cart.items.all())

        order = Order.objects.create(
            user=user,
            session_id=session_id,
            email=validated_data["email"],
            phone_number=validated_data.get("phone_number"),
            total_amount=total_amount
        )

        # Copy cart → order items
        order_items = [
            OrderItem(
                order=order,
                product_variant=item.product_variant,
                product_name=str(item.product_variant),
                price=item.price,
                quantity=item.quantity,
                total_price=item.total_price,
            )
            for item in cart.items.all()
        ]

        OrderItem.objects.bulk_create(order_items)

        return order

    def _get_cart(self, user, session_id):
        from apps.cart.models import Cart

        if user:
            return Cart.objects.filter(user=user).first()
        return Cart.objects.filter(session_id=session_id).first()


class OrderReadSerializer(ModelSerializer):
    items = OrderItemReadSerializer(many=True)

    class Meta:
        model = Order
        fields = [
            "id",
            "email",
            "phone_number",
            "status",
            "total_amount",
            "created_at",
            "items",
        ]
