from .base import *

DEBUG = False

ALLOWED_HOSTS += env.list('ALLOWED_HOSTS')

# CORs headers config
CORS_ALLOWED_ORIGINS = env.list('CORS_ALLOWED_ORIGINS')

CSRF_TRUSTED_ORIGINS = env.list('CSRF_TRUSTED_ORIGINS')

# Use ASGI on production
ASGI_APPLICATION = 'config.asgi.application'

# Cloudflare R2 Configuration
AWS_S3_ENDPOINT_URL = env('AWS_S3_ENDPOINT_URL')
AWS_ACCESS_KEY_ID = env('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = env('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = env('AWS_STORAGE_BUCKET_NAME')

# Configure for media files
DEFAULT_FILE_STORAGE = 'storages.backends.s3.S3Storage'

# Configure for static files
STATICFILES_STORAGE = 'storages.backends.s3.S3Storage' 

# Other S3 settings
AWS_S3_FILE_OVERWRITE = False  # Keep files, don't delete/overwrite

AWS_DEFAULT_ACL = None         # Use bucket policies, don't make public by default

# Make sure we handle media URL correctly
MEDIA_URL = f'{AWS_S3_ENDPOINT_URL}/{AWS_STORAGE_BUCKET_NAME}/media/'

# Cludinary configuration, used for image processing
# ie. resizing, compressing, & converting an image to 'webp' format.
cloudinary.config(
    cloud_name = env('CLOUDINARY_CLOUD_NAME'),
    api_key = env('CLOUDINARY_API_KEY'),
    api_secret = env('CLOUDINARY_API_SECRET'),
    secure = True # Ensures HTTPS URLs
)

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

# Celery config
REDIS_PASSWORD = env('REDIS_PASSWORD')
CELERY_BROKER_URL = f'redis://:{REDIS_PASSWORD}@redis:6379/0'

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# To allow request from Cross-SIte origin (as needed for APIs)
CSRF_COOKIE_SAMESITE = 'None'
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SAMESITE = 'None' # Allow cookies to be sent in cross-site requests
SESSION_COOKIE_SECURE = True  # Required when SameSite is 'None'

# We stream to STROUT, then we handle logs from the hosting platform
# Ensure only console is used
LOGGING["loggers"]["payments"]["handlers"] = ["console"]