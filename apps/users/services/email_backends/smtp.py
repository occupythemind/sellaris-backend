from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from apps.users.services.email_service import EmailService


class SMTPEmailService(EmailService):
    def send_email(self, to_email, subject, body, html_content):
        email = EmailMultiAlternatives(
            subject=subject,
            body=body,  # fallback
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[to_email],
        )

        email.attach_alternative(html_content, "text/html")
        email.send()