from .base import *

DEBUG = True
    
ALLOWED_HOSTS = ['https://4dv73f61-5173.euw.devtunnels.ms/', "localhost", "127.0.0.1", 'backend']
CSRF_TRUSTED_ORIGINS = [
    'https://4dv73f61-5173.euw.devtunnels.ms/',
    "http://127.0.0.1:8000",
    "http://127.0.0.1:5173",
    "http://localhost:8000",
]
CSRF_COOKIE_SECURE = False
SESSION_COOKIE_SECURE = False
CORS_ALLOWED_ORIGINS = [
    'https://4dv73f61-5173.euw.devtunnels.ms',
    "http://localhost:5173",
    "http://127.0.0.1:5173",

    "https://localhost:5173",
    "https://127.0.0.1:5173",
]
CORS_ALLOW_CREDENTIALS = True