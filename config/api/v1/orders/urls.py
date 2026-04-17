from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import OrderAPIView

# For non-trailing slash
router = DefaultRouter(trailing_slash=False)
router.register('checkout', OrderAPIView,basename='checkout')

urlpatterns = [
    path('', include(router.urls)),
]