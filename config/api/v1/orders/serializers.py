from django.db import transaction
from rest_framework.serializers import ModelSerializer, ValidationError

from apps.inventory.services import reserve_stock, confirm_stock, release_stock
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

        price_changes = []
        stock_changes = []

        cart_items = list(cart.items.select_related("product_variant"))

        # STEP 1: VALIDATE & AUTO-ADJUST
        for item in cart_items:
            variant = item.product_variant

            # --- PRICE CHECK ---
            current_price = variant.price
            if item.price != current_price:
                price_changes.append({
                    "product": str(variant),
                    "old_price": item.price,
                    "new_price": current_price
                })

                item.price = current_price

            # --- STOCK CHECK ---
            available = variant.stock_quantity - variant.reserved_stock

            if item.quantity > available:
                stock_changes.append({
                    "product": str(variant),
                    "requested": item.quantity,
                    "available": available
                })

                # auto-adjust (can go to 0)
                item.quantity = max(available, 0)

            # update total
            item.total_price = item.price * item.quantity

            item.save(update_fields=["price", "quantity", "total_price"])

        # RESERVE STOCK (SAFE)
        for item in cart_items:
            if item.quantity > 0:
                reserve_stock(
                    item.product_variant,
                    item.quantity
                )

        # CREATE ORDER
        valid_items = [item for item in cart_items if item.quantity > 0]

        # Check to make sure there is at least valid items
        if not valid_items:
            raise ValidationError({
                "error": "OUT_OF_STOCK",
                "message": "All items are out of stock",
                "stock_changes": stock_changes
            })

        total_amount = sum(item.total_price for item in valid_items)

        order = Order.objects.create(
            user=user,
            session_id=session_id,
            email=validated_data["email"],
            phone_number=validated_data.get("phone_number"),
            total_amount=total_amount
        )

        order_items = [
            OrderItem(
                order=order,
                product_variant=item.product_variant,
                product_name=str(item.product_variant),
                price=item.price,
                quantity=item.quantity,
                total_price=item.total_price,
            )
            for item in valid_items
        ]

        OrderItem.objects.bulk_create(order_items)

        # RESPONSE CONTEXT
        self.context["changes"] = {
            "price_changes": price_changes,
            "stock_changes": stock_changes
        }

        return order

    def to_representation(self, instance):
        data = super().to_representation(instance)

        changes = self.context.get("changes")

        if changes and (changes["price_changes"] or changes["stock_changes"]):
            data["changes"] = changes

        return data

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
