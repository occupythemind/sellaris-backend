from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CartAPIView, CartItemAPIView

router = DefaultRouter(trailing_slash=False)
router.register('carts', CartAPIView, basename='cart')
router.register('cart-items', CartItemAPIView, basename='cart-item')

urlpatterns = [
    path('', include(router.urls)),
]