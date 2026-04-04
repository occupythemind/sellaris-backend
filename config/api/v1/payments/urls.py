from django.urls import path
from .views import PaymentInitializeAPIView

urlpatterns = [
    path('initialize/', PaymentInitializeAPIView.as_view()),
]