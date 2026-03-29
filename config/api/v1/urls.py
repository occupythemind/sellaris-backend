from django.urls import path, include

urlpatterns = [
    path('products/', include('config.api.v1.products.urls')),
    path('carts/', include('config.api.v1.cart.urls')),
    path('wishlists/', include('config.api.v1.wishlists.urls')),
    path('orders/', include('config.api.v1.orders.urls')),
    path('payments/', include('config.api.v1.payments.urls')),
]