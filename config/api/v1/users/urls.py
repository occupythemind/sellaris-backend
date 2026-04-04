from django.urls import path
from .views import (
    RegisterAPIView,
    LoginAPIView,
    VerifyEmailAPIView,
    ResendVerificationAPIView,
    AccountAPIView,
    DeleteAccountAPIView,
    GoogleOAuthAPIView,
    FacebookOAuthAPIView,
    AppleOAuthAPIView,
)


urlpatterns = [
    path('register/', RegisterAPIView.as_view(), name='register'),
    path('login/', LoginAPIView.as_view(), name='login'),
    path('verify-email/', VerifyEmailAPIView.as_view(), name='verify-email'),
    path('resend-email-verify/', ResendVerificationAPIView.as_view(), name='resend-email-verify'),
    path('manage-account/', AccountAPIView.as_view(), name='manage-account'),
    path('delete', DeleteAccountAPIView.as_view(), name='delete-user'),
    path('google/', GoogleOAuthAPIView.as_view(), name='google'),
    path('facebook/', FacebookOAuthAPIView.as_view(), name='facebook'),
    path('apple/', AppleOAuthAPIView.as_view(), name='apple'),
]