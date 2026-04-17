from django.urls import path
from .views import PaymentInitializeAPIView, PaymentRecordListView

urlpatterns = [
    path('', PaymentRecordListView.as_view()),
    path('initialize', PaymentInitializeAPIView.as_view()),
]