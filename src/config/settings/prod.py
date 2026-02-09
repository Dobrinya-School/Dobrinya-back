from .base import *

DEBUG = False
ALLOWED_HOSTS = ["mydomain.com", "127.0.0.1", "localhost", "backend"]
CSRF_TRUSTED_ORIGINS = [
    "http://127.0.0.1:8000",
    "http://127.0.0.1:5173",
    "http://localhost:8000",
]
CSRF_COOKIE_SECURE = False
SESSION_COOKIE_SECURE = False
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]
CORS_ALLOW_CREDENTIALS = True