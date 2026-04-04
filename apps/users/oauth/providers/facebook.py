import requests
from django.conf import settings


class FacebookOAuthService:
    BASE_URL = "https://graph.facebook.com"

    def verify_token(self, token):
        try:
            # Validate token with Facebook
            debug_url = f"{self.BASE_URL}/debug_token"

            app_token = f"{settings.FACEBOOK_APP_ID}|{settings.FACEBOOK_APP_SECRET}"

            debug_response = requests.get(debug_url, params={
                "input_token": token,
                "access_token": app_token,
            })

            debug_data = debug_response.json().get("data", {})

            if not debug_data.get("is_valid"):
                return None

            # Ensure token belongs to our app
            if debug_data.get("app_id") != settings.FACEBOOK_APP_ID:
                return None

            user_id = debug_data.get("user_id")

            # Fetch user info
            user_response = requests.get(
                f"{self.BASE_URL}/me",
                params={
                    "fields": "id,name,email",
                    "access_token": token,
                }
            )

            user_info = user_response.json()

            return {
                "email": user_info.get("email"),
                "full_name": user_info.get("name"),
                "provider_user_id": user_info.get("id"),
                "is_verified": True,  # Facebook accounts are trusted
            }

        except Exception:
            return None