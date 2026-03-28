import requests
from django.conf import settings


class PaystackService:

    @staticmethod
    def initialize_payment(payment, customer_email):
        url = "https://api.paystack.co/transaction/initialize"

        headers = {
            "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
            "Content-Type": "application/json",
        }

        payload = {
            "email": customer_email,
            "amount": int(payment.amount * 100),  # Paystack uses kobo, not decimal (like Flutterwave)
            "reference": payment.reference_id,
            "callback_url": settings.PAYMENT_REDIRECT_URL,
            "currency": payment.currency,
        }

        response = requests.post(url, json=payload, headers=headers)
        data = response.json()

        if not data.get("status"):
            raise Exception("Paystack initialization failed")

        return data["data"]["authorization_url"]