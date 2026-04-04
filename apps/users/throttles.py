from rest_framework.throttling import SimpleRateThrottle


class LoginThrottle(SimpleRateThrottle):
    scope = "login"

    def get_cache_key(self, request, view):
        email = request.data.get("email", "")
        ident = self.get_ident(request)

        return f"login:{ident}:{email}"


class RegisterThrottle(SimpleRateThrottle):
    scope = "register"

    def get_cache_key(self, request, view):
        email = request.data.get("email", "")
        ident = self.get_ident(request)

        return f"login:{ident}:{email}"


class VerifyEmailThrottle(SimpleRateThrottle):
    scope = "verify_email"

    def get_cache_key(self, request, view):
        email = request.data.get("email", "")
        ident = self.get_ident(request)

        return f"login:{ident}:{email}"


class ResendVerificationThrottle(SimpleRateThrottle):
    scope = "resend_verification"

    def get_cache_key(self, request, view):
        email = request.data.get("email", "")
        ident = self.get_ident(request)

        return f"login:{ident}:{email}"
    

class OAuthThrottle(SimpleRateThrottle):
    scope = "oauth"

    def get_cache_key(self, request, view):
        token = request.data.get("token", "")
        ident = self.get_ident(request)

        return f"oauth:{ident}:{token[:10]}"  # partial token to avoid huge keys