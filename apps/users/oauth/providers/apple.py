import requests
from jose import jwt
from django.conf import settings


class AppleOAuthService:
    APPLE_KEYS_URL = "https://appleid.apple.com/auth/keys"

    def _get_apple_public_keys(self):
        response = requests.get(self.APPLE_KEYS_URL)
        response.raise_for_status()
        return response.json()["keys"]

    def verify_token(self, identity_token):
        try:
            headers = jwt.get_unverified_header(identity_token)
            kid = headers["kid"]

            keys = self._get_apple_public_keys()

            key = next((k for k in keys if k["kid"] == kid), None)

            if not key:
                return None

            public_key = jwt.algorithms.RSAAlgorithm.from_jwk(key)

            decoded = jwt.decode(
                identity_token,
                public_key,
                algorithms=["RS256"],
                audience=settings.APPLE_CLIENT_ID,
                issuer="https://appleid.apple.com",
            )

            return {
                "email": decoded.get("email"),
                "provider_user_id": decoded.get("sub"),
                "is_verified": True,
                "full_name": "",  # Apple doesn't reliably provide
            }

        except Exception:
            return None