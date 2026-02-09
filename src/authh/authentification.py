from rest_framework.authentication import SessionAuthentication
from datetime import timezone, timedelta
import base64
from io import BytesIO

from .models import *

MAX_FAILED_ATTEMPTS = 5
BLOCK_TIME_MINUTES = 15

class CsrfExemptSessionAuthentication(SessionAuthentication):
    def enforce_csrf(self, request):
        return

def generate_totp_qr_base64(uri):
    img = qrcode.make(uri)
    buf = BytesIO()
    img.save(buf, format="PNG")
    b64 = base64.b64encode(buf.getvalue()).decode()
    return f"data:image/png;base64,{b64}"

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0]
    return request.META.get('REMOTE_ADDR')

def requires_additional_verification(user, ip, user_agent):
    if not user.is_verified:
        return False

    now = timezone.now()
    recent_attempts = UserLoginAttempt.objects.filter(
        user=user,
        timestamp__gte=now - timedelta(minutes=BLOCK_TIME_MINUTES)
    )

    failed_count = recent_attempts.filter(successful=False, reason="password").count()

    last_login_ip = recent_attempts.filter(successful=True).last()
    suspicious = False
    if last_login_ip:
        if last_login_ip.ip_address != ip or last_login_ip.user_agent != user_agent:
            suspicious = True

    return failed_count >= MAX_FAILED_ATTEMPTS or suspicious