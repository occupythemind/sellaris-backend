import os
from celery import Celery

# Set default Django settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.dev")
app = Celery("config")

# Read config from Django settings, prefixed with "CELERY_"
app.config_from_object("django.conf:settings", namespace="CELERY")

# Auto-discover tasks in all apps
app.autodiscover_tasks()
