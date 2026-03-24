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

    def get_serializer_class(self):
        if self.action in ["list", "retrieve"]:
            return CategoryReadSerializer
        return CategoryWriteSerializer

class ProductViewSet(ModelViewSet):
    queryset = Product.objects.all()
    permission_classes = [IsStaffOrReadOnly]

    def get_serializer_class(self):
        if self.action in ["list", "retrieve"]:
            return ProductReadSerializer
        return ProductWriteSerializer

class ProductVariantViewSet(ModelViewSet):
    queryset = ProductVariant.objects.all()
    permission_classes = [IsStaffOrReadOnly]

    def get_serializer_class(self):
        if self.action in ["list", "retrieve"]:
            return ProductVariantReadSerializer
        return ProductVariantWriteSerializer

class SpecificationViewSet(ModelViewSet):
    queryset = Specification.objects.all()
    permission_classes = [IsStaffOrReadOnly]

    def get_serializer_class(self):
        if self.action in ["list", "retrieve"]:
            return SpecificationReadSerializer
        return SpecificationWriteSerializer
    
class ProductImageViewSet(ModelViewSet):
    queryset = ProductImage.objects.all()
    permission_classes = [IsStaffOrReadOnly]

    def get_serializer_class(self):
        if self.action in ["list", "retrieve"]:
            return ProductImageReadSerializer
        return ProductImageWriteSerializer