from django.db import transaction
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError, PermissionDenied
from rest_framework.response import Response
from django.conf import settings
from apps.orders.models import Order
from apps.payments.models import Payment, PaymentStatus
from apps.payments.services.factory import get_payment_service

    
class PaymentInitializeAPIView(APIView):

    @transaction.atomic
    def post(self, request):
        '''
        NOTE: This also requires `order_id`, and `provider` name
        ie. paystack or flutterwave
        '''
        order_id = request.data.get("order_id")

        order = Order.objects.select_for_update().get(id=order_id)

        # Ownership Check FIRST
        if request.user.is_authenticated:
            if order.user != request.user:
                raise PermissionDenied()
        else:
            if order.session_id != request.session.session_key:
                raise PermissionDenied()

        # Status Validation
        if order.status == "PAID":
            raise ValidationError("Order already paid")

        if order.status != "PENDING":
            raise ValidationError("Invalid order state")

        # IDEMPOTENCY CHECK
        existing_payment = Payment.objects.filter(
            order=order,
            status="INITIALIZED"
        ).first()

        if existing_payment:
            return Response({
                "payment_link": existing_payment.payment_link,
                "tx_ref": existing_payment.tx_ref,
                "message": "Reusing existing payment"
            })
        
        # PAYMENT PROVIDER VALIDATION
        provider, payment_service = get_payment_service(request.data.get("provider", "").strip())

        if not provider:
            raise ValidationError("Unsupported Payment Provider")
        
        # CREATE PAYMENT
        payment = Payment.objects.create(
            order=order,
            provider=provider,
            amount=order.total_amount,
            status=PaymentStatus.INITIALIZED
        )

        # CALL GATEWAY
        payment_link = payment_service.initialize_payment(
            payment=payment,
            customer_email=order.email
        )

        # STORE LINK, just incase an error occur, customer can try again
        payment.payment_link = payment_link
        payment.save(update_fields=["payment_link"])

        return Response({
            "payment_link": payment_link,
            "tx_ref": payment.tx_ref
        })
    