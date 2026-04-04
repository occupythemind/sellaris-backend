from django.db import transaction
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError, PermissionDenied
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from apps.orders.models import Order
from apps.payments.models import Payment, PaymentStatus
from apps.payments.services.factory import get_payment_service
import logging

logger = logging.getLogger("payments")
    
class PaymentInitializeAPIView(APIView):

    @transaction.atomic
    def post(self, request):
        '''
        NOTE: This also requires `order_id`, and `provider` name
        ie. paystack or flutterwave
        '''
        order_id = request.data.get("order_id", "")
        provider = str(request.data.get("provider", "")).strip()

        if not order_id:
            return Response(
                {"detail":"missing parameter: order_id"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not provider:
            return Response(
                {"detail":"missing parameter: provider"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if provider not in ["flutterwave", "paystack"]:
            return Response(
                {"detail":"Supported payment providers are 'flutterwave' or 'paystack'"},
                status=status.HTTP_400_BAD_REQUEST
            )

        order = Order.objects.select_for_update().get(id=order_id)

        # Ownership Check FIRST
        if request.user.is_authenticated:
            if order.user != request.user:
                raise PermissionDenied()
        else:
            if order.session_id != request.session.session_key:
                raise PermissionDenied()

        # Status Validation
        if order.status.upper() == "PAID":
            raise ValidationError("Order already paid")

        if order.status.upper() != "PENDING":
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
        payment_service = get_payment_service(provider)
        
        # CREATE PAYMENT
        payment = Payment.objects.create(
            order=order,
            provider=provider,
            amount=order.total_amount,
            status=PaymentStatus.INITIALIZED
        )

        logger.info(f"Payment created: {payment.reference_id}")

        # CALL GATEWAY
        payment_link = payment_service.initialize_payment(
            payment=payment,
            customer_email=order.email
        )

        logger.info(f"Payment initialized: {payment.reference_id}")

        # STORE LINK, just incase an error occur, customer can try again
        payment.payment_link = payment_link
        payment.save(update_fields=["payment_link"])

        return Response({
            "payment_link": payment_link,
            "reference_id": payment.reference_id
        })
    