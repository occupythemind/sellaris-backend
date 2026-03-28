from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import OrderAPIView

router = DefaultRouter()
router.register('checkout', OrderAPIView,basename='checkout')

urlpatterns = [
    path('', include(router.urls))
]