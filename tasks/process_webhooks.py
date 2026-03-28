from rest_framework.response import Response
from celery import shared_task
from django.conf import settings
from django.utils import timezone
import requests
import json

from apps.payments.models import Payment, PaymentStatus

@shared_task(bind=True, max_retries=3)
def process_flutterwave_webhook(self, payload, log):
    try:
        # Parse event
        data = json.loads(payload)
        event = data.get("event")

        if event != "charge.completed":
            return Response(status=200)
        
        # Fetch payment data
        payment_data = data["data"]
        tx_ref = payment_data["tx_ref"]
        flw_tx_id = payment_data["id"]

        # Fetch payment safely
        payment = Payment.objects.select_related("order").filter(
            reference_id=tx_ref
        ).first()

        if not payment:
            log.status = "failed"
            log.detail = "payment object not found"
            log.save(update_fields=["status", "detail"])
            return Response(status=200)
        
        # Idempotency check
        if payment.status == PaymentStatus.SUCCESS:
            return Response(status=200)
        
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
            payment.save(update_fields=["status"])
            log.status = "failed"
            log.detail = "non matching records"
            log.save(update_fields=["status", "detail"])
            return Response(status=200)
        
        # Mark payment successful if it passed these checks
        payment.status = PaymentStatus.SUCCESS
        payment.transaction_id = str(flw_tx_id)
        payment.confirmed_at = timezone.now()
        payment.save()

        order = payment.order
        order.status = "PAID"
        order.save(update_fields=["status"])

    except Exception as e:
        raise self.retry(exc=e, countdown=10)
    

@shared_task(bind=True, max_retries=3)
def process_paystack_webhook(self, payload):
    try:
        event = payload.get("event")

        if event != "charge.success":
            return

        data = payload["data"]

        reference = data["reference"]

        payment = Payment.objects.select_related("order").filter(
            reference_id=reference
        ).first()

        if not payment:
            return

        # IDEMPOTENCY
        if payment.status == PaymentStatus.SUCCESS:
            return

        # VERIFY WITH PAYSTACK
        url = f"https://api.paystack.co/transaction/verify/{reference}"

        headers = {
            "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}"
        }

        response = requests.get(url, headers=headers)
        verify_data = response.json()

        if not verify_data.get("status"):
            raise Exception("Verification failed")

        verified = verify_data["data"]

        # VALIDATION
        if (
            verified["amount"] != int(payment.amount * 100) or
            verified["currency"] != payment.currency or
            verified["reference"] != payment.reference_id
        ):
            payment.status = PaymentStatus.FAILED
            payment.save(update_fields=["status"])
            return

        # SUCCESS
        payment.status = PaymentStatus.SUCCESS
        payment.transaction_id = str(verified["id"])
        payment.confirmed_at = timezone.now()
        payment.save()

        order = payment.order
        order.status = "PAID"
        order.save(update_fields=["status"])

    except Exception as e:
        raise self.retry(exc=e, countdown=10)