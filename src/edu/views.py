from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.forms.models import model_to_dict

from authh.authentification import *
from .models import *

@api_view(['GET'])
@authentication_classes([CsrfExemptSessionAuthentication])
@permission_classes([IsAuthenticated])
def profile(request):
    userprofile = UserProfile.objects.filter(user=request.user).first()
    if userprofile:
        data = model_to_dict(userprofile)
        data["email"] = str(userprofile.user)
        print({"status": "ok", "profile": data})
        return Response({"status": "ok", "profile": data}, status=200)
    return Response({"status": "error", "detail": "Профиль пользователя не найден"}, status=404)
    
@api_view(['GET'])
@authentication_classes([CsrfExemptSessionAuthentication])
@permission_classes([IsAuthenticated])
def publicprofile(request, user_id):
    userprofile = UserProfile.objects.filter(user=user_id).first()
    if userprofile:
        data = model_to_dict(userprofile)
        del data["user"]
        print({"status": "ok", "profile": data})
        return Response({"status": "ok", "profile": data}, status=200)
    return Response({"status": "error", "detail": "Профиль пользователя не найден"}, status=404)

@api_view(['GET'])
@authentication_classes([CsrfExemptSessionAuthentication])
@permission_classes([IsAuthenticated])
def roleprofile(request, user_id):
    user = User.objects.filter(id=user_id).first()
    if not user:
        return Response({"status": "error", "detail": "Неверный id пользователя"}, status=403)
    profile = TeacherProfile.objects.filter(user=user).first() or \
        StudentProfile.objects.filter(user=user).first()
    if profile:
        user_role = "teacher" if isinstance(profile, TeacherProfile) else "student"
        data = model_to_dict(profile)
        del data["user"]
        if user_role == "student":
            data['school_class'] = str(profile.school_class)
        return Response({"status": "ok", "role": user_role, "profile": data})
    return Response({"status": "error", "detail": "Профиль пользователя не найден"})

@api_view(['GET'])
@authentication_classes([CsrfExemptSessionAuthentication])
@permission_classes([IsAuthenticated])
def classstudents(request, class_id):
    teacher = TeacherProfile.objects.filter(user=request.user).first()
    if not teacher:
        return Response({"status": "error", "detail": "Вы не учитель"}, status=403)
    class_ = SchoolClass.objects.filter(id=class_id).first()
    if not class_:
        return Response({"status": "error", "detail": "Неверный id класса"}, status=404)
    
    students_data = []
    for student in class_.students:
        data = {}
        user_profile = UserProfile.objects.filter(user=student.user).first()
        if user_profile:
            user_data = model_to_dict(user_profile)
            del user_data["user"]
            data = data | user_data
        student_data = model_to_dict(student)
        del student_data["user"]
        student_data['school_class'] = str(profile.school_class)
        data = data | student_data

        students_data.append(data)
    
    data = {"name": class_.name, "year": class_.year, "students": students_data}
    return Response({"status": "ok", "students": students_data})

@api_view(['GET'])
@authentication_classes([CsrfExemptSessionAuthentication])
@permission_classes([IsAuthenticated])
def classprofile(request, class_id):
    teacher = TeacherProfile.objects.filter(user=request.user).first()
    if not teacher:
        return Response({"status": "error", "detail": "Вы не учитель"}, status=403)
    class_ = SchoolClass.objects.filter(id=class_id).first()
    if not class_:
        return Response({"status": "error", "detail": "Неверный id класса"}, status=403)
    
    data = {"name": class_.name, "year": class_.year}
    return Response({"status": "ok", "profile": data})
