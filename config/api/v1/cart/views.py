from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from apps.cart.models import (
    Cart,
    CartItem,
)
from .serializers import (
    CartReadSerializer,
    CartWriteSerializer,
    CartItemReadSerializer,
    CartItemWriteSerializer,
)


class CartAPIView(ModelViewSet):
    queryset = Cart.objects.all()
    permission_classes = [AllowAny]

    def get_serializer_class(self):
        if self.action in ["list", "retrieve"]:
            return CartReadSerializer
        return CartWriteSerializer

    def get_queryset(self):
        request = self.request

        if request.user.is_authenticated:
            return Cart.objects.filter(user=request.user)

        session_id = request.session.session_key
        return Cart.objects.filter(session_id=session_id)

    def _get_or_create_cart(self):
        request = self.request

        if request.user.is_authenticated:
            cart, _ = Cart.objects.get_or_create(user=request.user)
            return cart

        # Ensure session exists
        if not request.session.session_key:
            request.session.create()

        session_id = request.session.session_key

        cart, _ = Cart.objects.get_or_create(session_id=session_id)
        return cart

    def list(self, request, *args, **kwargs):
        cart = self._get_or_create_cart()
        serializer = self.get_serializer(cart)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        # Prevent accessing other carts
        cart = self._get_or_create_cart()
        serializer = self.get_serializer(cart)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        # Disable direct cart creation
        return Response(
            {"detail": "Not allowed."},
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )
    
    def update(self, request, *args, **kwargs):
        # Disable direct cart creation
        return Response(
            {"detail": "Not allowed."},
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )
    
    def partial_update(self, request, *args, **kwargs):
        # Disable direct cart creation
        return Response(
            {"detail": "Not allowed."},
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )

    def destroy(self, request, *args, **kwargs):
        cart = self._get_or_create_cart()
        cart.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

  
class CartItemAPIView(ModelViewSet):
    queryset = CartItem.objects.all()
    permission_classes = [AllowAny]

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]

    # Filtering
    filterset_fields = [
        "product_variant",
        "product_variant__product",
    ]

    # Search
    search_fields = [
        "product_variant__product__name",
        "product_variant__product__brand",
        "product_variant__color",
        "product_variant__sku_code",
    ]

    # Ordering
    ordering_fields = [
        "quantity",
        "price",
        "created_at",
    ]
    ordering = ["-created_at"]

    def get_serializer_class(self):
        if self.action in ["list", "retrieve"]:
            return CartItemReadSerializer
        return CartItemWriteSerializer

    # Helpers
    def _get_cart(self):
        request = self.request

        if request.user.is_authenticated:
            cart, _ = Cart.objects.get_or_create(user=request.user)
            return cart

        if not request.session.session_key:
            request.session.create()

        session_id = request.session.session_key
        cart, _ = Cart.objects.get_or_create(session_id=session_id)
        return cart

    # Query restriction
    def get_queryset(self):
        cart = self._get_cart()
        return (
            CartItem.objects
            .filter(cart=cart)
            .select_related("product_variant", "product_variant__product")
        )

    # Create (Add to cart)
    def create(self, request, *args, **kwargs):
        cart = self._get_cart()

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        item = serializer.save(cart=cart)

        return Response(
            CartItemReadSerializer(item).data,
            status=status.HTTP_201_CREATED
        )

    def update(self, request, *args, **kwargs):
        instance = self.get_object()

        serializer = self.get_serializer(
            instance,
            data=request.data
        )
        serializer.is_valid(raise_exception=True)

        item = serializer.save()

        return Response(
            CartItemReadSerializer(item).data,
            status=status.HTTP_200_OK
        )

    # Partial update
    def partial_update(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    # Delete item
    def destroy(self, request, *args, **kwargs):
        item = self.get_object()
        item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)