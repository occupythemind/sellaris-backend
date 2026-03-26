from django.shortcuts import get_object_or_404
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import AllowAny
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Prefetch

from apps.wishlists.models import Wishlist, WishlistItem
from .serializers import (
    WishlistReadSerializer,
    WishlistWriteSerializer,
    WishlistItemReadSerializer,
    WishlistItemWriteSerializer,
)

class WishlistViewSet(ModelViewSet):
    permission_classes = [AllowAny]

    def get_queryset(self):
        """
            Returns wishlists based on the request context:
            - Logged-in users: own wishlists
            - Guests: session-based wishlists
            - Optional: ?from=others returns other users' public wishlists
        """
        user = self.request.user
        session_id = self.request.session.session_key

        # Ensure session exists for guests
        if not session_id:
            self.request.session.create()
            session_id = self.request.session.session_key

        # Base queryset with prefetch
        queryset = Wishlist.objects.prefetch_related(
            Prefetch(
                "items",
                queryset=WishlistItem.objects.select_related("product_variant")
            )
        )

        # Check for special query parameter
        show_others = self.request.query_params.get("from") == "others"

        if user.is_authenticated:
            if show_others:
                # Return public wishlists NOT belonging to the current user
                queryset = queryset.filter(is_public=True).exclude(user=user)
            else:
                # Own wishlists
                queryset = queryset.filter(user=user)
        else:
            if show_others:
                # Public wishlists from other users only
                queryset = queryset.filter(is_public=True).exclude(session_id=session_id)
            else:
                # Guest's own session wishlists
                queryset = queryset.filter(session_id=session_id)

        return queryset

    def get_serializer_class(self):
        if self.action in ["list", "retrieve"]:
            return WishlistReadSerializer
        return WishlistWriteSerializer
    
    def retrieve(self, request, *args, **kwargs):
        """
            Retrieve a public wishlist by ID (for shareable links or public view).
        """
        wishlist_id = kwargs.get("pk")  # DRF passes URL param as 'pk'
        wishlist = get_object_or_404(Wishlist, id=wishlist_id)
        if (not wishlist.is_public
            ) and (self.request.user != wishlist.user and self.request.session != wishlist.session_id):
            return Response(
                {"detail": "No Wishlist matches the given query."}, 
                status=status.HTTP_404_NOT_FOUND
                )
        
        serializer = WishlistReadSerializer(wishlist, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def perform_create(self, serializer):
        user = self.request.user

        if user.is_authenticated:
            serializer.save(user=user)
        else:
            session_id = self.request.session.session_key

            if not session_id:
                self.request.session.create()
                session_id = self.request.session.session_key

            serializer.save(session_id=session_id)

    def perform_update(self, serializer):
        wishlist = serializer.instance

        # Wishlist is not owned by the user and is not public
        if wishlist.user != self.request.user and not wishlist.is_public:
            raise NotFound("Wishlist not found.")

        # Wishlist is public but not owned by the user
        if wishlist.user != self.request.user and wishlist.is_public:
            raise PermissionDenied("You do not have permission to update this wishlist.")

        # Owned by the user
        serializer.save()

    def perform_destroy(self, instance):
        # Wishlist is not owned by the user and is not public
        if instance.user != self.request.user and not instance.is_public:
            raise NotFound("Wishlist not found.")

        # Wishlist is public but not owned by the user
        if instance.user != self.request.user and instance.is_public:
            raise PermissionDenied("You do not have permission to delete this wishlist.")

        # Owned by the user
        instance.delete()

class WishlistItemViewSet(ModelViewSet):
    permission_classes = [AllowAny]

    def get_queryset(self):
        user = self.request.user
        session_id = self.request.session.session_key

        queryset = WishlistItem.objects.select_related("product_variant", "wishlist")

        if user.is_authenticated:
            queryset = queryset.filter(wishlist__user=user)
        else:
            # Ensure session exists
            if not session_id:
                self.request.session.create()
                session_id = self.request.session.session_key
            queryset = queryset.filter(wishlist__session_id=session_id)

        return queryset

    def get_serializer_class(self):
        if self.action in ["list", "retrieve"]:
            return WishlistItemReadSerializer
        return WishlistItemWriteSerializer

    def perform_create(self, serializer):
        wishlist = serializer.validated_data.get("wishlist")
        user = self.request.user
        session_id = self.request.session.session_key

        # Ensure session exists for guests
        if not session_id:
            self.request.session.create()
            session_id = self.request.session.session_key

        # Wishlist is not owned and not public
        if wishlist.user != user and not wishlist.is_public:
            raise NotFound("Wishlist not found.")

        # Wishlist is public but not owned
        if wishlist.user != user and wishlist.is_public:
            raise PermissionDenied("You do not have permission to add items to this wishlist.")

        # Wishlist is owned by the user (or guest owns the session)
        if not user.is_authenticated and wishlist.session_id != session_id:
            raise NotFound("Wishlist not found.")

        serializer.save()

    def perform_destroy(self, instance):
        wishlist = instance.wishlist
        user = self.request.user
        session_id = self.request.session.session_key

        # Ensure session exists for guests
        if not session_id:
            self.request.session.create()
            session_id = self.request.session.session_key

        # Wishlist is not owned and not public
        if wishlist.user != user and not wishlist.is_public:
            raise NotFound("Wishlist item not found.")

        # Wishlist is public but not owned
        if wishlist.user != user and wishlist.is_public:
            raise PermissionDenied("You do not have permission to delete items from this wishlist.")

        # Wishlist is owned by the user (or guest owns the session)
        if not user.is_authenticated and wishlist.session_id != session_id:
            raise NotFound("Wishlist item not found.")

        instance.delete()