from django.contrib.auth import get_user_model
from django.db import transaction

from apps.users.models import UserAuthProvider

User = get_user_model()


class OAuthService:
    @transaction.atomic
    def handle_oauth_login(self, provider, user_data):
        email = user_data["email"]

        # Check if provider already exists
        provider_obj = UserAuthProvider.objects.filter(
            provider=provider,
            provider_user_id=user_data["provider_user_id"]
        ).select_related("user").first()

        if provider_obj:
            return provider_obj.user

        # Check if user exists by email (link account)
        user = User.objects.filter(email=email).first()

        if not user:
            # Create new user
            user = User.objects.create(
                email=email,
                full_name=user_data.get("full_name", ""),
                is_verified=True  # OAuth emails are trusted
            )

        # Link provider
        UserAuthProvider.objects.create(
            user=user,
            provider=provider,
            provider_user_id=user_data["provider_user_id"]
        )

        return user