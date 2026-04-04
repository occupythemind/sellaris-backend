from django.conf import settings

from .email_backends.smtp import SMTPEmailService
from .email_backends.sendpulse import SendPulseEmailService


def get_email_service():
    provider = getattr(settings, "EMAIL_PROVIDER", "smtp")

    if provider == "smtp":
        return SMTPEmailService()
    
    elif provider == "sendpulse":
        return SendPulseEmailService()

    raise ValueError("Unsupported email provider")