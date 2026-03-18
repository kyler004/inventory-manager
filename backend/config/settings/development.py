from .base import *

DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# Allow React dev server to talk to Django
CORS_ALLOWED_ORIGINS = [
    'http://localhost:5173',
]

# Use console email backend in dev (prints emails to terminal)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'