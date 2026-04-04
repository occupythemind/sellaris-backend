from django.conf import settings


class EmailService:
    def send_email(self, to_email, subject, body):
        raise NotImplementedError