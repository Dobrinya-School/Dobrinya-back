"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView
from rest_framework.schemas import get_schema_view
from rest_framework.renderers import JSONOpenAPIRenderer

from journal import urls as journal_urls
from authh import urls as auth_urls
from edu import urls as edu_urls

schema_view = get_schema_view(
    title="My API",
    version="1.0.0",
    renderer_classes=[JSONOpenAPIRenderer],
)

urlpatterns = [
    path('schema/', schema_view, name='schema'),
    path('redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

    path('admin/', admin.site.urls),
    path("journal/", include((journal_urls, "journal"), namespace="journal")),
    path("auth/", include((auth_urls, "auth"), namespace="auth")),
    path("edu/", include((edu_urls, "edu"), namespace="edu")),
]
