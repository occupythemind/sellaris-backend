from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.urls import reverse
from django.conf import settings
from django.template.loader import render_to_string

from apps.users.tokens import email_verification_token
from .email_factory import get_email_service


def send_verification_email(user):
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = email_verification_token.make_token(user)

    verify_url = f"{settings.EMAIL_VERIFY_URL}?uid={uid}&token={token}"

    if settings.DEBUG:
        html_content = render_to_string(
            "emails/verify_email_dev.html",
            {"verify_url": verify_url}
        )
    else:
        html_content = render_to_string(
            "emails/verify_email_prod.html",
            {"verify_url": verify_url}
        )

    subject = "Verify your email"
    body = f"Click to verify your email: {verify_url}" # fallback

    email_service = get_email_service()
    email_service.send_email(user.email, subject, body, html_content)