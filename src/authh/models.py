from django.contrib.auth.models import AbstractBaseUser
from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin
from django.utils import timezone
from django.core.signing import TimestampSigner, BadSignature, SignatureExpired

import uuid
import secrets
import pyotp
import qrcode

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email: raise ValueError("Email must be set")

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_verified", True)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        return self.create_user(email, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(null=False, unique=True)
    password = models.CharField(max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    # email_verification_token = models.CharField(max_length=64, null=True, blank=True)
    telegram_id = models.CharField(max_length=32, null=True, blank=True, unique=True)
    telegram_enabled = models.BooleanField(default=False)
    totp_secret = models.CharField(max_length=32, null=True, blank=True)
    totp_enabled = models.BooleanField(default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        # db_table = "auth.users"
        verbose_name = "User"
        verbose_name_plural = "Users"

        # managed = False

    def __str__(self):
        return self.email

    @classmethod
    def exists(cls, email: str) -> bool:
        return cls.objects.filter(email=email).exists()

    def generate_email_token(self):
        signer = TimestampSigner()
        token = signer.sign(self.pk)
        return token

    @staticmethod
    def verify_email_token(token, max_age=60*60*24):
        signer = TimestampSigner()
        try:
            user_id = signer.unsign(token, max_age=max_age)
            return User.objects.get(pk=user_id)
        except (BadSignature, SignatureExpired, User.DoesNotExist):
            return None

    def gen_secret(self): return pyotp.random_base32()

    def totp_url(self):
        return pyotp.totp.TOTP(self.totp_secret).provisioning_uri(
            name=self.email, issuer_name="Dobrinya"
        )

    def verify_totp(self, code):
        totp = pyotp.TOTP(self.totp_secret)
        return totp.verify(code, valid_window=1)
    
class UserLoginAttempt(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey("authh.User", on_delete=models.CASCADE, related_name="login_attempts")
    timestamp = models.DateTimeField(default=timezone.now)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)
    successful = models.BooleanField(default=False)
    reason = models.CharField(max_length=64, blank=True)

class LoginSession(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()

    stage = models.CharField(
        max_length=32,
        choices=[
            ("password_ok", "Password OK"),
            ("totp_pending", "TOTP Pending"),
            ("telegram_pending", "Telegram Pending"),
            ("completed", "Completed"),
        ]
    )

    expires_at = models.DateTimeField()
    attempts = models.PositiveSmallIntegerField(default=0)