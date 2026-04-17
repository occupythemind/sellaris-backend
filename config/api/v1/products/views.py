from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.viewsets import ModelViewSet
from core.permissions import IsStaffOrReadOnly
from apps.products.models import (
    Category, 
    Product,
    ProductVariant,
    Specification,
    ProductImage,
)
from .serializers import (
    CategoryReadSerializer, 
    CategoryWriteSerializer, 
    ProductReadSerializer, 
    ProductWriteSerializer,
    ProductVariantReadSerializer,
    ProductVariantWriteSerializer,
    SpecificationReadSerializer,
    SpecificationWriteSerializer,
    ProductImageReadSerializer,
    ProductImageWriteSerializer,
)

# To Be Tested via BurpSuite


class CategoryViewSet(ModelViewSet):
    queryset = Category.objects.all()
    permission_classes = [IsStaffOrReadOnly]

    filter_backends = [DjangoFilterBackend, SearchFilter]
    search_fields = ["name"]

    def get_serializer_class(self):
        if self.action in ["list", "retrieve"]:
            return CategoryReadSerializer
        return CategoryWriteSerializer


class ProductViewSet(ModelViewSet):
    queryset = Product.objects.select_related("category").all()
    permission_classes = [IsStaffOrReadOnly]

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]

    # Filtering
    filterset_fields = ["category", "brand", "currency"]

    # Searching
    search_fields = ["name", "brand", "description"]

    # Ordering
    ordering_fields = ["base_price", "name"]
    ordering = ["-base_price"]  # default

    def get_serializer_class(self):
        if self.action in ["list", "retrieve"]:
            return ProductReadSerializer
        return ProductWriteSerializer


class ProductVariantViewSet(ModelViewSet):
    queryset = ProductVariant.objects.select_related("product").all()
    permission_classes = [IsStaffOrReadOnly]

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]

    filterset_fields = [
        "product",
        "color",
        "storage_size",
        "currency",
    ]

    search_fields = [
        "product__name",
        "sku_code",
        "color",
    ]

    ordering_fields = ["price", "stock_quantity"]
    ordering = ["price"]

    def get_serializer_class(self):
        if self.action in ["list", "retrieve"]:
            return ProductVariantReadSerializer
        return ProductVariantWriteSerializer


class SpecificationViewSet(ModelViewSet):
    queryset = Specification.objects.select_related("product_variant").all()
    permission_classes = [IsStaffOrReadOnly]

    filter_backends = [DjangoFilterBackend, SearchFilter]

    filterset_fields = ["product_variant", "name"]
    search_fields = ["name", "value"]

    def get_serializer_class(self):
        if self.action in ["list", "retrieve"]:
            return SpecificationReadSerializer
        return SpecificationWriteSerializer


class ProductImageViewSet(ModelViewSet):
    queryset = ProductImage.objects.select_related("product_variant").all()
    permission_classes = [IsStaffOrReadOnly]

    filter_backends = [DjangoFilterBackend]

    filterset_fields = ["product_variant", "is_main"]

    def get_serializer_class(self):
        if self.action in ["list", "retrieve"]:
            return ProductImageReadSerializer
        return ProductImageWriteSerializer