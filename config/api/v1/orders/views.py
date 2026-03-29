from rest_framework.mixins import CreateModelMixin, RetrieveModelMixin
from rest_framework.viewsets import GenericViewSet
from rest_framework.permissions import AllowAny
from django.db import transaction
from apps.orders.models import Order
from .serializers import OrderReadSerializer, OrderWriteSerializer


class OrderAPIView(CreateModelMixin,
                   RetrieveModelMixin,
                   GenericViewSet):
    permission_classes = [AllowAny]

    def get_queryset(self):
        user = self.request.user

        if user.is_authenticated:
            return Order.objects.filter(user=user)

        return Order.objects.filter(session_id=self.request.session.session_key)

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