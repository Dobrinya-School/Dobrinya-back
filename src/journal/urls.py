from django.urls import path, include

from .views import *

urlpatterns = [
    path("students/", StudentsView.as_view(), name="students")
]