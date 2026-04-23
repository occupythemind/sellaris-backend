from celery import shared_task
from django.contrib.auth import get_user_model
import logging

from apps.users.services.verification_service import send_verification_email

logger = logging.getLogger("users")

User = get_user_model()


@shared_task(bind=True, max_retries=3, queue="emails")
def send_verification_email_task(self, user_id, request_origin):
    try:
        user = User.objects.get(id=user_id)

        logger.info(f"Sending verification email to {user.email}")

        send_verification_email(user, request_origin)
    except Exception as exc:
        logger.error(f"Email sending failed for user {user_id}: {exc}")
        raise self.retry(exc=exc, countdown=60)