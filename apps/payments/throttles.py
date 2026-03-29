from rest_framework.throttling import SimpleRateThrottle

class FlutterwaveWebhookThrottle(SimpleRateThrottle):
    scope = "flutterwave_webhook"

    def get_cache_key(self, request, view):
        return "flutterwave-webhook"
    
class PaystackWebhookThrottle(SimpleRateThrottle):
    scope = "paystack_webhook"

    def get_cache_key(self, request, view):
        return "paystack-webhook"