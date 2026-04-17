"""
URL configuration for config project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# The APIs are accessible via a domain or subdomain dedicated 
# to the API server eg., api.example.com or api-example.com etc.
urlpatterns = [
    # So both /v1/ and /api/v1/ can work seemlessly
    path('v1/', include('config.api.v1.urls')),
    path('api/v1/', include('config.api.v1.urls')),
    path('payments/webhook', include('apps.payments.urls')),
]

# Only include login/logout for browsable API in DEBUG mode
if settings.DEBUG:
    urlpatterns += [
        path('admin/', admin.site.urls),
        path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    ]

# Only include media file serving in DEBUG mode (dev environment)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)