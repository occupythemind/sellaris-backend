from .flutterwave import FlutterwaveService
from .paystack import PaystackService

def get_payment_service(provider: str):
    if provider == "flutterwave":
        return ("flutterwave", FlutterwaveService())
    elif provider == "paystack":
        return ("paystack", PaystackService())
    return None