from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from django.conf import settings


class GoogleOAuthService:
    def verify_token(self, token):
        try:
            # VALIDATE SIGNATURE & CHECK EXPIRY
            idinfo = id_token.verify_oauth2_token(
                token,
                google_requests.Request(),
                settings.GOOGLE_CLIENT_ID
            )

            return {
                "email": idinfo.get("email"),
                "full_name": idinfo.get("name"),
                "provider_user_id": idinfo.get("sub"),
                "is_verified": idinfo.get("email_verified", False),
            }

        except Exception:
            return None