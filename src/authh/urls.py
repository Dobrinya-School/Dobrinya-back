from django.urls import path, include

from .views import *

urlpatterns = [
    path("me/", me, name="me"),

    path("verify/", verify_email_view, name="verify_email"),

    path("totp-setup/", totp_setup_start, name="totp_setup"),
    path("totp-enable/", totp_setup_confirm, name="totp_enable"),
    path("verify-totp/", verify_totp_view, name="verify_totp"),

    path("verify-telegram/", verify_totp_view, name="verify_telegram"),

    path("register/", register_view, name="register"),
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout")
]