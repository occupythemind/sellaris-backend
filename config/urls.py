"""
URL configuration for config project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings

# The APIs are accessible via a domain or subdomain dedicated 
# to the API server eg., api.example.com or api-example.com etc.
urlpatterns = [
    path('v1/', include('config.api.v1.urls')),
    path('payments/webhook/', include('apps.payments.urls')),
]

# Only include login/logout for browsable API in DEBUG mode
if settings.DEBUG:
    urlpatterns += [
        path('admin/', admin.site.urls),
        path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    ]