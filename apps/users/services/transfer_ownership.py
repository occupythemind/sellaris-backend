from django.db import transaction, models
from apps.cart.models import Cart, CartItem
from apps.wishlists.models import Wishlist
from apps.orders.models import Order


@transaction.atomic
def transfer_guest_data_to_user(request, user):
    session_id = request.session.session_key

    if not session_id:
        return

    _transfer_wishlist(session_id, user)
    _merge_cart(session_id, user)
    _transfer_orders(session_id, user)


def _transfer_wishlist(session_id, user):
    Wishlist.objects.filter(
        session_id=session_id,
        user__isnull=True
    ).update(user=user, session_id=None)


def _merge_cart(session_id, user):
    # Lock both carts in consistent order to avoid deadlocks
    carts = list(
        Cart.objects.select_for_update()
        .filter(
            (models.Q(session_id=session_id, user__isnull=True)) |
            (models.Q(user=user))
        )
        .order_by("id")  # consistent locking order
    )

    guest_cart = None
    user_cart = None

    for cart in carts:
        if cart.user_id == user.id:
            user_cart = cart
        elif cart.session_id == session_id:
            guest_cart = cart

    if not guest_cart:
        return

    if not user_cart:
        guest_cart.user = user
        guest_cart.session_id = None
        guest_cart.save()
        return

    # Lock cart items too
    guest_items = list(
        guest_cart.items.select_for_update().all()
    )

    user_items = {
        item.product_variant_id: item
        for item in user_cart.items.select_for_update()
    }

    for guest_item in guest_items:
        existing_item = user_items.get(guest_item.product_variant_id)

        if existing_item:
            existing_item.quantity += guest_item.quantity
            existing_item.save(update_fields=["quantity"])
        else:
            guest_item.cart = user_cart
            guest_item.save(update_fields=["cart"])

    guest_cart.delete()


def _transfer_orders(session_id, user):
    Order.objects.select_for_update().filter(
        session_id=session_id,
        user__isnull=True,
        status="PENDING"
    ).update(user=user, session_id=None)