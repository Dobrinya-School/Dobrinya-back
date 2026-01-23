from .base import *

DEBUG = False
ALLOWED_HOSTS = ["mydomain.com", "127.0.0.1", "localhost", "web"]
CSRF_TRUSTED_ORIGINS = [
    "http://127.0.0.1:8000",
    "http://localhost:8000",
]
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'http')