import requests
from decimal import Decimal
from django.conf import settings


class PaystackService:

    @staticmethod
    def initialize_payment(payment, customer_email, request_origin):
        url = "https://api.paystack.co/transaction/initialize"

        headers = {
            "Authorization": f"Bearer {settings.PST_SECRET_KEY}",
            "Content-Type": "application/json",
        }

        payload = {
            "email": customer_email,
            "amount": int(Decimal(payment.amount) * 100),  # Paystack uses kobo, not decimal (like Flutterwave)
            "reference": payment.reference_id,
            "callback_url": request_origin + settings.PAYMENT_REDIRECT_PATH,
            "currency": payment.currency,
        }

        response = requests.post(url, json=payload, headers=headers)
        data = response.json()

        if not data.get("status"):
            raise Exception(data.get("message"))

        return data["data"]["authorization_url"]