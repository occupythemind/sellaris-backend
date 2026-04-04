from .flutterwave import FlutterwaveService
from .paystack import PaystackService

def get_payment_service(provider: str):
    if provider == "flutterwave":
        return FlutterwaveService()
    elif provider == "paystack":
        return PaystackService()
    return None