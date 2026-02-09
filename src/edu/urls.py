from django.urls import path, include

from .views import *

urlpatterns = [
    path("profile/", profile, name="profile"),

    path("public/role/<uuid:user_id>/", roleprofile, name="role-profile"),
    path("public/profile/<uuid:user_id>/", publicprofile, name="user-profile"),

    path("public/class/<uuid:user_id>/", classprofile, name="class-profile"),
    path("public/class/<uuid:user_id>/students/", classstudents, name="class-students"),
]