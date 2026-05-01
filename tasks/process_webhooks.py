from rest_framework.response import Response
from celery import shared_task
from django.conf import settings
from django.db import transaction
from django.utils import timezone
from decimal import Decimal
import requests
import json
import logging

from apps.payments.models import (
    Payment, 
    PaymentStatus, 
    PaymentWebhookLog
)
from apps.orders.models import OrderStatus
from apps.inventory.services import confirm_stock


logger = logging.getLogger("payments")


@shared_task(bind=True, max_retries=3)
@transaction.atomic
def process_flutterwave_webhook(self, payload, log_id):
    tx_ref = None
    try:
        log = PaymentWebhookLog.objects.get(id=log_id)

        # Parse event
        if isinstance(payload, (str, bytes)):
            data = json.loads(payload)
        else:
            data = payload
            
        event = data.get("event")

        if event != "charge.completed":
            return
        
        # Fetch payment data
        payment_data = data["data"]
        tx_ref = payment_data["tx_ref"]
        flw_tx_id = payment_data["id"]

        logger.info(f"Processing payment webhook: {tx_ref}")

        # Fetch payment safely
        payment = Payment.objects.select_related("order").filter(
            reference_id=tx_ref
        ).first()

        if not payment:
            log.status = "failed"
            log.detail = "payment object not found"
            log.save(update_fields=["status", "detail"])
            return
        
        # Idempotency check
        if payment.status == PaymentStatus.SUCCESS:
            return
        
        # Verify with Flutterwave API
        verify_url = f"{settings.FLW_BASE_URL}/transactions/{flw_tx_id}/verify"

        headers = {
            "Authorization": f"Bearer {settings.FLW_SECRET_KEY}"
        }

        response = requests.get(verify_url, headers=headers)
        verify_data = response.json()

        verified = verify_data["data"]

        # Validate Everything to ensure it matches with our existing record
        if (
            verify_data["status"] != "success" or
            verified["amount"] != payment.amount or
            verified["currency"] != payment.currency or
            verified["tx_ref"] != payment.reference_id
        ):
            payment.status = PaymentStatus.FAILED
            payment.transaction_id = flw_tx_id
            payment.save(update_fields=["status", "transaction_id"])
            log.status = "failed"
            log.detail = "non matching records"
            log.save(update_fields=["status", "detail"])
            return
        
        # SUCCESS
        payment.status = PaymentStatus.SUCCESS
        payment.transaction_id = str(flw_tx_id)
        payment.confirmed_at = timezone.now()
        payment.save()
        
        # Update the Log after processing
        log.status = "success"
        log.processed = True
        log.save(update_fields=["status", "processed"])

        order = payment.order
        if order.status.upper() != "PENDING":
            return
        order.status = OrderStatus.PAID
        order.save(update_fields=["status"])
        
        # Update ProductVariant stock quantity
        for item in order.items.select_related("product_variant"):
            confirm_stock(item.product_variant, item.quantity)

    except Exception as e:
        logger.error("Payment verification failed", exc_info=True)
        raise self.retry(exc=e, countdown=10)
    

@shared_task(bind=True, max_retries=3)
@transaction.atomic
def process_paystack_webhook(self, payload, log_id):
    reference = None
    try:
        log = PaymentWebhookLog.objects.get(id=log_id)

        # Parse payload if it's a string or bytes
        if isinstance(payload, (str, bytes)):
            payload = json.loads(payload)

        event = payload.get("event")

        if event != "charge.success":
            return

        data = payload["data"]

        reference = data["reference"]
        pst_tx_id = data["id"]

        logger.info(f"Processing payment webhook: {reference}")

        payment = Payment.objects.select_related("order").filter(
            reference_id=reference
        ).first()

        if not payment:
            log.status = "failed"
            log.detail = "payment object not found"
            log.save(update_fields=["status", "detail"])
            return

        # IDEMPOTENCY
        if payment.status == PaymentStatus.SUCCESS:
            return

        # VERIFY WITH PAYSTACK
        url = f"https://api.paystack.co/transaction/verify/{reference}"

        headers = {
            "Authorization": f"Bearer {settings.PST_SECRET_KEY}"
        }

        response = requests.get(url, headers=headers)
        verify_data = response.json()

        if not verify_data.get("status"):
            raise Exception("Verification failed")

        verified = verify_data["data"]

        # VALIDATION
        if (
            verified["amount"] != int(Decimal(payment.amount) * 100) or
            verified["currency"] != payment.currency or
            verified["reference"] != payment.reference_id
        ):
            payment.status = PaymentStatus.FAILED
            payment.transaction_id = pst_tx_id
            payment.save(update_fields=["status", "transaction_id"])
            log.status = "failed"
            log.detail = "non matching records"
            log.save(update_fields=["status", "detail"])
            return

        # SUCCESS
        payment.status = PaymentStatus.SUCCESS
        payment.transaction_id = str(verified["id"])
        payment.confirmed_at = timezone.now()
        payment.save()

        # Update the Log after processing
        log.status = "success"
        log.processed = True
        log.save(update_fields=["status", "processed"])

        order = payment.order
        if order.status.upper() != "PENDING":
            return
        order.status = OrderStatus.PAID
        order.save(update_fields=["status"])

        # Update ProductVariant stock quantity
        for item in order.items.select_related("product_variant"):
            confirm_stock(item.product_variant, item.quantity)

    except Exception as e:
        logger.error(
            f"Paystack webhook failed for ref={reference}",
            exc_info=True
        )
        raise self.retry(exc=e, countdown=10)