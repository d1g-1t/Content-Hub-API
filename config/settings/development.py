"""
Development settings for Content Hub API.
"""
from .base import *  # noqa

DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0']

# Development-specific apps
INSTALLED_APPS += [
    'debug_toolbar',
]

MIDDLEWARE += [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]

# Debug Toolbar settings
INTERNAL_IPS = [
    '127.0.0.1',
    'localhost',
]

# Disable some security features in development
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

# Email backend for development (console)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Development logging - more verbose
LOGGING['root']['level'] = 'DEBUG'  # noqa
LOGGING['loggers']['django']['level'] = 'DEBUG'  # noqa
LOGGING['loggers']['apps']['level'] = 'DEBUG'  # noqa
