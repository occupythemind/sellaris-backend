"""
WSGI config for config project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

# Check environment variable, default to dev for development
settings_module = os.environ.get('DJANGO_SETTINGS_MODULE')
if not settings_module:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.dev')
else:
    os.environ['DJANGO_SETTINGS_MODULE'] = settings_module

application = get_wsgi_application()
