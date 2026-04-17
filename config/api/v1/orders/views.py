from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.mixins import (
    CreateModelMixin, 
    RetrieveModelMixin,
    ListModelMixin,
)
from rest_framework.viewsets import GenericViewSet
from rest_framework.permissions import AllowAny
from django.db import transaction
from apps.orders.models import Order
from .serializers import OrderReadSerializer, OrderWriteSerializer


class OrderAPIView(CreateModelMixin,
                   RetrieveModelMixin,
                   ListModelMixin,
                   GenericViewSet):
    permission_classes = [AllowAny]

    # ENABLE FILTERING / SEARCH / ORDERING
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]

    filterset_fields = ["status", "currency"]
    search_fields = ["email", "phone_number", "id"]
    ordering_fields = ["created_at", "total_amount"]
    ordering = ["-created_at"]  # default

    def get_queryset(self):
        user = self.request.user

        if user.is_authenticated:
            return Order.objects.filter(user=user)

        session_key = self.request.session.session_key
        if not session_key:
            return Order.objects.none()

        return Order.objects.filter(session_id=session_key)

    def get_serializer_class(self):
        if self.action == "create":
            return OrderWriteSerializer
        return OrderReadSerializer

    @transaction.atomic
    def perform_create(self, serializer):
        order = serializer.save()

        # We DO NOT clear cart here yet, rather we
        # wait until payment is confirmed, for good UX

        return order