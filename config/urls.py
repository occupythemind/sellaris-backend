"""
URL configuration for config project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings

urlpatterns = [
    path('api/v1/', include('config.api.v1.urls')),
]

# Only include login/logout for browsable API in DEBUG mode
if settings.DEBUG:
    urlpatterns += [
        path('admin/', admin.site.urls),
        path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    ]