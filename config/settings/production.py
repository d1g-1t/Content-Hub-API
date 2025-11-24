"""
Production settings for Content Hub API.
"""
from .base import *  # noqa

DEBUG = False

# Security Settings
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Production cache settings
CACHES['default']['OPTIONS']['PARSER_CLASS'] = 'redis.connection.HiredisParser'  # noqa

# Production logging
LOGGING['handlers']['file']['filename'] = '/var/log/django/content_hub.log'  # noqa

# Email backend for production
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = env('EMAIL_HOST', default='smtp.gmail.com')  # noqa
EMAIL_PORT = env.int('EMAIL_PORT', default=587)  # noqa
EMAIL_USE_TLS = True
EMAIL_HOST_USER = env('EMAIL_HOST_USER', default='')  # noqa
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD', default='')  # noqa

# Static files - use whitenoise or similar in production
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'
