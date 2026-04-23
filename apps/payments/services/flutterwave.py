from django.conf import settings
import requests
import logging

logger = logging.getLogger("payments")

class FlutterwaveService:

    @staticmethod
    def initialize_payment(payment, customer_email, request_origin):
        url = f"{settings.FLW_BASE_URL}/payments"

        headers = {
            "Authorization": f"Bearer {settings.FLW_SECRET_KEY}",
            "Content-Type": "application/json"
        }

        payload = {
            "tx_ref": payment.reference_id,
            "amount": str(payment.amount),
            "currency": payment.currency,
            # For the user's browser (frontend), not webhook URL
            "redirect_url": request_origin + settings.PAYMENT_REDIRECT_PATH,
            "customer": {
                "email": customer_email
            },
            "customizations": {
                "title": settings.EMAIL_FROM_NAME,
            }
        }

        response = requests.post(url, json=payload, headers=headers)
        data = response.json()

        if response.status_code != 200 or data.get("status") != "success":
            raise Exception("Payment initialization failed")

        return data["data"]["link"]
    