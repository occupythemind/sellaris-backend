from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CategoryViewSet,
    ProductViewSet,
    ProductVariantViewSet,
    SpecificationViewSet,
    ProductImageViewSet,
)

router = DefaultRouter()
router.register('categories', CategoryViewSet, basename='category')
router.register('products', ProductViewSet, basename='product')
router.register('product-variants', ProductVariantViewSet, basename='product-variant')
router.register('specifications', SpecificationViewSet, basename='specification')
router.register('product-images', ProductImageViewSet, basename='product-image')

urlpatterns = [
    path('', include(router.urls)),
]