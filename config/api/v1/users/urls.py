from django.urls import path
from .views import (
    RegisterAPIView,
    LoginAPIView,
    get_csrf,
    VerifyEmailAPIView,
    ResendVerificationAPIView,
    AccountUpdateAPIView,
    AccountInfoAPIView,
    DeleteAccountAPIView,
    GoogleOAuthAPIView,
    FacebookOAuthAPIView,
    AppleOAuthAPIView,
)


urlpatterns = [
    path('register', RegisterAPIView.as_view(), name='register'),
    path('login', LoginAPIView.as_view(), name='login'),
    path("users/get-csrf/", get_csrf),
    path('verify-email', VerifyEmailAPIView.as_view(), name='verify-email'),
    path('resend-email-verify', ResendVerificationAPIView.as_view(), name='resend-email-verify'),
    path('account-info', AccountInfoAPIView.as_view(), name='account-info'),
    path('manage-account', AccountUpdateAPIView.as_view(), name='manage-account'),
    path('delete', DeleteAccountAPIView.as_view(), name='delete-user'),
    path('google', GoogleOAuthAPIView.as_view(), name='google'),
    path('facebook', FacebookOAuthAPIView.as_view(), name='facebook'),
    path('apple', AppleOAuthAPIView.as_view(), name='apple'),
]