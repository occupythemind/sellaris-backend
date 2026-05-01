from django.db import transaction
from apps.products.models import ProductVariant
from .models import InventoryLog


@transaction.atomic
def set_stock(variant_id, quantity, user=None):
    variant = ProductVariant.objects.select_for_update().get(id=variant_id)

    prev = variant.stock_quantity
    variant.stock_quantity = quantity
    variant.save()

    InventoryLog.objects.create(
        product_variant=variant,
        action="SET",
        quantity=quantity,
        previous_stock=prev,
        new_stock=variant.stock_quantity,
        performed_by=user
    )


@transaction.atomic
def adjust_stock(variant_id, quantity, action, user=None):
    variant = ProductVariant.objects.select_for_update().get(id=variant_id)

    prev = variant.stock_quantity

    if action == "INCREASE":
        variant.stock_quantity += quantity
    elif action == "DECREASE":
        if quantity > variant.stock_quantity:
            raise Exception("Cannot reduce below zero")
        variant.stock_quantity -= quantity

    variant.save()

    InventoryLog.objects.create(
        product_variant=variant,
        action=action,
        quantity=quantity,
        previous_stock=prev,
        new_stock=variant.stock_quantity,
        performed_by=user
    )


@transaction.atomic
def reserve_stock(variant, quantity):
    '''ON ORDER CREATION
    Reserve stock, rather than just deducting them from the productVariant stock
    '''

    variant = ProductVariant.objects.select_for_update().get(id=variant.id)

    prev = variant.stock_quantity
    available = variant.stock_quantity - variant.reserved_stock

    if quantity > available:
        raise Exception("Insufficient stock")

    variant.reserved_stock += quantity
    variant.save()

    InventoryLog.objects.create(
        product_variant=variant,
        action="RESERVE",
        quantity=quantity,
        previous_stock=prev,
        new_stock=variant.stock_quantity,
        note="Reserved for order"
    )


@transaction.atomic
def confirm_stock(variant, quantity):
    '''ON PAYMENT SUCCESS
    Deduct stock after payment is confirmed (successful)
    '''

    variant = ProductVariant.objects.select_for_update().get(id=variant.id)

    prev = variant.stock_quantity
    variant.stock_quantity -= quantity
    variant.reserved_stock -= quantity

    variant.save()

    InventoryLog.objects.create(
        product_variant=variant,
        action="CONFIRM",
        quantity=quantity,
        previous_stock=prev,
        new_stock=variant.stock_quantity,
        note="Payment Successful"
    )


@transaction.atomic
def release_stock(variant, quantity):
    '''ON PAYMENT FAILURE/TIMEOUT
    Release stock if payment fails or timeout
    '''
    variant = ProductVariant.objects.select_for_update().get(id=variant.id)

    prev = variant.stock_quantity
    variant.reserved_stock -= quantity
    variant.save()

    InventoryLog.objects.create(
        product_variant=variant,
        action="RELEASE",
        quantity=quantity,
        previous_stock=prev,
        new_stock=variant.stock_quantity,
        note="Order Expired"
    )
