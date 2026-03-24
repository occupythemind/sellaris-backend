from .base import *

DEBUG = True
ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# Local storage
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'