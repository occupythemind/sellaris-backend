from .base import *

DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# CORs headers config
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5500",  # Common port for VS Code Live Server
    "http://127.0.0.1:5500",
]

INSTALLED_APPS += ['rest_framework',]

# Local storage
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Log config
LOGGING["handlers"]["file"] = {
    "class": "logging.handlers.RotatingFileHandler",
    "filename": "logs/payments.log",
    "maxBytes": 10 * 1024 * 1024,
    "backupCount": 5,
    "formatter": "standard",
}

LOGGING["loggers"]["payments"]["handlers"].append("file")