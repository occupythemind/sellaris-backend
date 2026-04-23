from .base import *

DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# CORs headers config
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5500",  # Common port for VS Code Live Server
    "http://127.0.0.1:5500",
]

CSRF_TRUSTED_ORIGINS = [
    "http://localhost:5500",  # Common port for VS Code Live Server
    "http://127.0.0.1:5500",
]

# IMPORTANT: This must be False if you want JavaScript to read the cookie
# If True, JS cannot see the cookie, and your X-CSRFToken header will be empty
CSRF_COOKIE_HTTPONLY = False 

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