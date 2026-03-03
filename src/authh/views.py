from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate, login, logout
from django.core.mail import send_mail
from django.forms.models import model_to_dict

from .authentification import *
from accounts.permissions import IsAuthorized
from .models import *

@api_view(['GET'])
@authentication_classes([CsrfExemptSessionAuthentication])
@permission_classes([IsAuthorized])
def me(request):
    user = request.user
    return Response({"status": "ok", "id": str(user.id)})

@api_view(['POST'])
@authentication_classes([CsrfExemptSessionAuthentication])
def verify_email_view(request):
    key = request.data.get('code')
    print(key)
    user = User.verify_email_token(key)
    if not user:
        return Response({"status": "error", "detail": "Ссылка недействительна или устарела"}, status=400)

    user.is_verified = True
    user.save()
    return Response({"status": "ok", "detail": "Почта подтверждена"}, status=200)

@api_view(["POST"])
@authentication_classes([CsrfExemptSessionAuthentication])
def verify_totp_view(request):
    session_id = request.data.get("login_session")
    print(session_id)
    code = request.data.get("code")

    session = LoginSession.objects.filter(id=session_id,expires_at__gt=timezone.now()).first()
    if not session: return Response({"status": "error", "detail": "Неверный id сессии"}, status=400)

    if not session.user.verify_totp(code):
        session.attempts += 1
        session.save()
        return Response({"status": "error", "detail": "Неверный TOTP код"}, status=400)

    login(request, session.user)
    session.stage = "completed"
    session.save()

    return Response({"status": "ok", "detail": "Успешный вход"})

@api_view(["POST"])
@authentication_classes([CsrfExemptSessionAuthentication])
@permission_classes([IsAuthorized])
def totp_setup_start(request):
    user = request.user

    if user.totp_enabled:
        return Response({"status": "error", "detail": "TOTP уже включен"}, status=400)

    if not user.totp_secret:
        user.totp_secret = user.gen_secret()
        user.save(update_fields=["totp_secret"])

    uri = user.totp_url()
    qr = generate_totp_qr_base64(uri)

    return Response({
        "status": "ok",
        "qr": qr,
        "detail": "Наведите камеру телефона на QR код"
    })

@api_view(["POST"])
@authentication_classes([CsrfExemptSessionAuthentication])
@permission_classes([IsAuthorized])
def totp_setup_confirm(request):
    code = request.data.get("code")
    user = request.user

    if not user.verify_totp(code):
        return Response({"status": "error", "detail": "Неверный код"}, status=400)

    user.totp_enabled = True
    user.save(update_fields=["totp_enabled"])

    return Response({"status": "ok"})


@api_view(['POST'])
@authentication_classes([CsrfExemptSessionAuthentication])
def register_view(request):
    email = request.data.get('email')
    password = request.data.get('password')

    if not email or not password:
        return Response({"status": "error", "detail": "Необходимы email и password"}, status=400)
    if User.exists(email):
        user = User.objects.create_user(email=email, password=password)
        ip = get_client_ip(request=request)
        ua = request.META.get('HTTP_USER_AGENT', '')
        UserLoginAttempt.objects.create(
            user=User.objects.filter(email=email).first(),
            ip_address=ip,
            user_agent=ua,
            successful=bool(user),
            reason=""
        )
        if user:
            if not user.is_verified:
                token = user.generate_email_token()
                print(f'http://127.0.0.1/auth/verify?code={token}')
                try:
                    send_mail(
                    "Подтверждение почты",
                    f"Для подтверждения почты перейдите по ссылке http://127.0.0.1/auth/verify?key={token}",
                    "from@example.com",
                    [user.email],
                    fail_silently=False,
                    )
                except Exception as e: print(e)

                return Response(
                {
                    "status": "email_verification_required",
                    "detail": f"Письмо отправлено на почту {user.email}. Ожидаем подтверждения",
                }, status=200)

@api_view(['POST'])
@authentication_classes([CsrfExemptSessionAuthentication])
def login_view(request):
    email = request.data.get('email')
    password = request.data.get('password')

    if not email or not password:
        return Response({"detail": "Необходимы email и password"}, status=400)

    if User.exists(email):
        user = authenticate(request, email=email, password=password)
        ip = get_client_ip(request=request)
        ua = request.META.get('HTTP_USER_AGENT', '')
        UserLoginAttempt.objects.create(
            user=User.objects.filter(email=email).first(),
            ip_address=ip,
            user_agent=ua,
            successful=bool(user),
            reason="password" if not bool(user) else ""
        )
        if user:
            if not user.is_active: return Response({"status": "error", "detail": "Аккаунт заблокирован"}, status=403)
            if not user.is_verified:
                token = user.generate_email_token()
                print(f'http://127.0.0.1/auth/verify?code={token}')
                try:
                    send_mail(
                    "Подтверждение почты",
                    f"Для подтверждения почты перейдите по ссылке http://127.0.0.1/auth/verify?key={token}",
                    "from@example.com",
                    [user.email],
                    fail_silently=False,
                    )
                except Exception as e: print(e)

                return Response(
                {
                    "status": "email_verification_required",
                    "detail": f"Письмо отправлено на почту {user.email}. Ожидаем подтверждения",
                }, status=200)

            if requires_additional_verification(user, ip, ua):

                session = LoginSession.objects.create(
                    user=user,
                    ip_address=ip,
                    user_agent=ua,
                    stage="password_ok",
                    expires_at=timezone.now() + timedelta(minutes=5)
                )

                UserLoginAttempt.objects.create(
                    user=user, ip_address=ip, user_agent=ua, successful=False, reason="additional_verification"
                )
                return Response({
                    "status": "additional_verification_required",
                    "detail": "Нужно подтверждение 2FA",
                    "variants": [
                        v for v, enabled in (
                            ("telegram", user.telegram_enabled),
                            ("totp", user.totp_enabled),
                        )
                        if enabled
                    ] or ["email"],
                    "login_session": str(session.id)
                }, status=200)

            login(request, user)
            return Response({"status": "ok", "detail": "Успешный вход"}, status=200)
        else:
            return Response({"status": "error", "detail": "Неверный пароль"}, status=401)
    else:
        return Response({"status": "error", "detail": "Аккаунта с таким email не существует"}, status=404)

@api_view(['POST'])
@authentication_classes([CsrfExemptSessionAuthentication])
@permission_classes([IsAuthorized])
def logout_view(request):
    logout(request)
    return Response({"status": "ok", "detail": "Logged out"}, status=status.HTTP_200_OK)
