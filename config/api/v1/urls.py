from django.urls import path, include

urlpatterns = [
    path('products/', include('config.api.v1.products.urls')),
]