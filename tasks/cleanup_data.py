from celery import shared_task
from django.utils import timezone
from datetime import timedelta

from apps.cart.models import Cart
from apps.wishlists.models import Wishlist
from apps.orders.models import Order

from core.utils import batch_delete


@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=True, max_retries=3)
def cleanup_expired_guest_data(self):
    now = timezone.now()

    # carts
    cart_qs = Cart.objects.filter(
        user__isnull=True,
        updated_at__lt=now - timedelta(days=14)
    )
    batch_delete(cart_qs, batch_size=500)

    # wishlists
    wishlist_qs = Wishlist.objects.filter(
        user__isnull=True,
        created_at__lt=now - timedelta(days=30)
    )
    batch_delete(wishlist_qs, batch_size=500)

    # pending orders
    order_qs = Order.objects.filter(
        user__isnull=True,
        status="PENDING",
        created_at__lt=now - timedelta(hours=48)
    )
    batch_delete(order_qs, batch_size=200)