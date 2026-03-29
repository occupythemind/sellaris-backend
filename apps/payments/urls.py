from django.urls import path
from .views import FlutterwaveWebhookAPIView, PaystackWebhookAPIView

urlpatterns = [
    path('flutterwave/', FlutterwaveWebhookAPIView.as_view()),
    path('paystack/', PaystackWebhookAPIView.as_view()),
]