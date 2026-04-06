from celery import shared_task
from django.utils import timezone
from datetime import timedelta
import logging

from apps.cart.models import Cart
from apps.wishlists.models import Wishlist
from apps.orders.models import Order
from apps.users.models import User
from apps.inventory.services import release_stock

from core.utils import batch_delete


logger = logging.getLogger("tasks")

@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=True, max_retries=3)
def cleanup_expired_guest_data(self):
    now = timezone.now()

    logger.info("Expired guest data in undergoing cleanup...")

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

    logger.info("Expired guest data cleaned up successfully")


@shared_task
def delete_user_account(user_id):
    try:

        user = User.objects.get(id=user_id)
        
        logger.info(f"User account {user_id}:{user.username} undergoing deletion...")
        
        # Only delete if still inactive
        if not user.is_active:
            user.delete()
            logger.info(f"User account {user_id}:{user.username} was deleted successfully")

    except User.DoesNotExist:
        pass


@shared_task
def release_expired_reservations():
    '''Release reserved stocks from "pending" orders made 40 minutes earlier, or more.'''
    from django.utils import timezone
    from datetime import timedelta

    expired_orders = Order.objects.filter(
        status="PENDING",
        created_at__lt=timezone.now() - timedelta(minutes=40)
    )

    logger.info("Expired Reservations undergoing deletion...")

    for order in expired_orders:
        for item in order.items.select_related("product_variant"):
            release_stock(
                item.product_variant, 
                item.quantity
            )

        order.status = "CANCELLED"
        order.save()

    logger.info("Expired Reservation has been released")