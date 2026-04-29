import requests
from decimal import Decimal
from django.conf import settings


class PaystackService:

    @staticmethod
    def initialize_payment(payment, customer_email, payment_redirect):
        url = "https://api.paystack.co/transaction/initialize"

        headers = {
            "Authorization": f"Bearer {settings.PST_SECRET_KEY}",
            "Content-Type": "application/json",
        }

        payload = {
            "email": customer_email,
            "amount": int(Decimal(payment.amount) * 100),  # Paystack uses kobo, not decimal (like Flutterwave)
            "reference": payment.reference_id,
            "callback_url": payment_redirect,
            "currency": payment.currency,
        }

        response = requests.post(url, json=payload, headers=headers)
        data = response.json()

        # For detailed error message for easy debugging on production
        try:
            data = response.json()
        except Exception:
            data = response.text

        if response.status_code != 200 or not data.get("status"):
            raise Exception(f"Paystack init failed ({response.status_code}): {data}")

        return data["data"]["authorization_url"]