from rest_framework.serializers import ModelSerializer, ValidationError
from rest_framework.validators import UniqueTogetherValidator
from apps.wishlists.models import Wishlist, WishlistItem


# Wishlist Items

class WishlistItemWriteSerializer(ModelSerializer):
    class Meta:
        model = WishlistItem
        fields = ["id", "wishlist", "product_variant"]
        validators = [
            UniqueTogetherValidator(
                queryset=WishlistItem.objects.all(),
                fields=["wishlist", "product_variant"],
                message="This product variant is already in the wishlist."
            )
        ]


class WishlistItemReadSerializer(ModelSerializer):
    class Meta:
        model = WishlistItem
        fields = [
            "id",
            "product_variant",
            "added_at",
        ]


# Wishlist

class WishlistWriteSerializer(ModelSerializer):
    class Meta:
        model = Wishlist
        fields = ["id", "name", "is_public"]

    def validate_name(self, value):
        """
        Prevent duplicate wishlist names for both guests and users.
        """
        user = self.context["request"].user
        session_id = self.context["request"].session.session_key

        qs = Wishlist.objects.filter(name=value)

        if user.is_authenticated:
            qs = qs.filter(user=user)
        else:
            if not session_id:
                # Create session if it doesn’t exist
                self.context["request"].session.create()
                session_id = self.context["request"].session.session_key
            qs = qs.filter(session_id=session_id)

        # Exclude current instance for updates
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)

        if qs.exists():
            raise ValidationError("You already have a wishlist with this name.")

        return value

class WishlistReadSerializer(ModelSerializer):
    items = WishlistItemReadSerializer(many=True, read_only=True)

    class Meta:
        model = Wishlist
        fields = [
            "id",
            "name",
            "is_public",
            "items",
            "created_at",
            "updated_at",
        ]


