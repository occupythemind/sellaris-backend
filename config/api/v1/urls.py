from django.urls import path, include

urlpatterns = [
    path('products/', include('config.api.v1.products.urls')),
    path('carts/', include('config.api.v1.cart.urls')),
]