from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from django.conf import settings
import hashlib
import hmac
import json
from tasks.process_webhooks import process_flutterwave_webhook, process_paystack_webhook
from .models import PaymentWebhookLog
from .throttles import FlutterwaveWebhookThrottle, PaystackWebhookThrottle


class FlutterwaveWebhookAPIView(APIView):
    throttle_classes = [FlutterwaveWebhookThrottle]

    def post(self, request):
        payload = request.body

        # VERIFY HASH, for authenticity & integrity
        signature = request.headers.get("verif-hash")

        if not signature:
            return Response(status=400)

        expected_hash = settings.FLW_SECRET_HASH  # set this in dashboard

        if not hmac.compare_digest(signature, expected_hash):
            return Response(status=403)
        
        # We LOG this before any processing
        log = PaymentWebhookLog.objects.create(
            provider="flutterwave",
            payload=json.loads(request.body),
            headers=dict(request.headers)
        )
        
        # SEND TO CELERY
        process_flutterwave_webhook.delay(payload, log)

        log.status = "queued"
        log.save(update_fields=["status"])

        return Response(status=200)


class PaystackWebhookAPIView(APIView):
    throttle_classes = [PaystackWebhookThrottle]

    def post(self, request):
        payload = request.body
        signature = request.headers.get("x-paystack-signature")

        # VERIFY SIGNATURE
        computed_hash = hmac.new(
            settings.PAYSTACK_SECRET_KEY.encode(),
            payload,
            hashlib.sha512
        ).hexdigest()

        if computed_hash != signature:
            return Response(status=403)

        data = json.loads(payload)

        # LOG FIRST
        log = PaymentWebhookLog.objects.create(
            provider="paystack",
            payload=data,
            headers=dict(request.headers),
            status="received"
        )

        # QUEUE TASK
        process_paystack_webhook.delay(data, log)

        log.status = "queued"
        log.save(update_fields=["status"])

        return Response(status=200)