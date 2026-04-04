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
        return CartItem.objects.filter(cart=cart).select_related("product_variant")

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

    # Update quantity
    def update(self, request, *args, **kwargs):
        item = self.get_object()

        quantity = int(request.data.get("quantity"))

        if quantity is None or int(quantity) <= 0:
            return Response(
                {"detail": "Quantity must be greater than 0"},
                status=status.HTTP_400_BAD_REQUEST
            )

        item.quantity = quantity
        item.save(update_fields=["quantity"])

        return Response(CartItemReadSerializer(item).data)

    # Partial update
    def partial_update(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    # Delete item
    def destroy(self, request, *args, **kwargs):
        item = self.get_object()
        item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)