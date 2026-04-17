from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import WishlistViewSet, WishlistItemViewSet

# For non-trailing slash
router = DefaultRouter(trailing_slash=False)
router.register('wishlists', WishlistViewSet, basename='wishlist')
router.register('wishlist-items', WishlistItemViewSet, basename='wishlist-item')

urlpatterns = [
    path('', include(router.urls)),
]