from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework import status
from django.forms.models import model_to_dict
from django.apps import apps

from accounts.utils import *
from accounts.permissions import *
from authh.authentification import CsrfExemptSessionAuthentication
from .models import *

User = apps.get_model("authh", "User")
UserProfile = apps.get_model("accounts", "UserProfile")

@api_view(['GET'])
@authentication_classes([CsrfExemptSessionAuthentication])
@permission_classes([IsAuthorized])
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
@permission_classes([IsAuthorized])
def publicprofile(request, user_id):
    userprofile = UserProfile.objects.filter(user=user_id).first()
    if userprofile:
        data = model_to_dict(userprofile)
        print({"status": "ok", "profile": data})
        return Response({"status": "ok", "profile": data}, status=200)
    return Response({"status": "error", "detail": "Профиль пользователя не найден"}, status=404)

@api_view(['GET'])
@authentication_classes([CsrfExemptSessionAuthentication])
@permission_classes([IsAuthorized, HasRole])
def roleprofile(request, user_id):
    user = User.objects.get(id=user_id)
    res = get_user_role(user_id=user.id, with_profile=True)
    user_role, profile = res[0], res[1]
    data = model_to_dict(profile)
    if user_role == "student":
        data['school_class'] = str(profile.school_class)
        data["school"] = profile.school_class.school.id
        data["school_name"] = profile.school_class.school.name
    else:
        data["school"] = profile.school.id
        data["school_name"] = profile.school.name
    return Response({"status": "ok", "role": user_role, "profile": data})

@api_view(['GET'])
@authentication_classes([CsrfExemptSessionAuthentication])
@permission_classes([IsAuthorized, HasRole])
def cities(request):
    cities = School.objects.values_list("city")
    print({"status": "ok", "cities": cities})
    return Response({"status": "ok", "cities": cities})

@api_view(['GET'])
@authentication_classes([CsrfExemptSessionAuthentication])
@permission_classes([IsAuthorized, HasRole])
def schools(request):
    city = request.GET.get("city")
    if not city:
        raise RPCPermissionDenied(detail="city не найден")
    schools = School.objects.filter(city=city).values_list("name", "city", "id")
    return Response({"status": "ok", "schools": schools})

@api_view(['GET'])
@authentication_classes([CsrfExemptSessionAuthentication])
@permission_classes([IsAuthorized, HasRole])
def schoolprofile(request, school_id):
    school = School.objects.get(id=school_id)
    return Response({"status": "ok", "school": model_to_dict(school)})

@api_view(['GET'])
@authentication_classes([CsrfExemptSessionAuthentication])
@permission_classes([IsAuthorized, HasRole])
def classes(request, school_id):
    classes = list(SchoolClass.objects.filter(school=school_id).values_list("name", "year", "id"))
    return Response({"status": "ok", "classes": classes})

@api_view(['GET'])
@authentication_classes([CsrfExemptSessionAuthentication])
@permission_classes([IsAuthorized, HasClassAccess])
def classstudents(request, class_id):
    class_ = SchoolClass.objects.get(id=class_id)
    
    students_data = []
    for student in class_.students.all():
        user_profile = UserProfile.objects.filter(user=student.user).first()
        if user_profile:
            data = {
            "user": student.user.id,
            "first_name": user_profile.first_name if user_profile else None,
            "last_name": user_profile.last_name if user_profile else None,
            "patronymic": user_profile.patronymic if user_profile else None,
            "avatar_url": user_profile.avatar_url if user_profile else None,
            "school_class": class_.name,
            }

            students_data.append(data)

    return Response({"status": "ok", "students": students_data})

@api_view(['GET'])
@authentication_classes([CsrfExemptSessionAuthentication])
@permission_classes([IsAuthorized, HasClassAccess])
def classprofile(request, class_id):
    class_ = SchoolClass.objects.get(id=class_id)
    
    data = {"id": class_.id, "name": class_.name, "year": class_.year}
    return Response({"status": "ok", "profile": data})

@api_view(['GET'])
@authentication_classes([CsrfExemptSessionAuthentication])
@permission_classes([IsAuthorized, HasClassAccess])
def classsubjects(request, class_id):
    subjects = ClassSubject.objects.filter(school_class=class_id).select_related("school_class", "subject", "teacher")
    res = []
    for subj in subjects: 
        data = {}
        profile = UserProfile.objects.get(user=subj.teacher.user)
        data["id"] = subj.id
        data["teacher"] = { "user": subj.teacher.user.id,
                           "first_name": profile.first_name,
                           "last_name": profile.last_name,
                           "patronymic": profile.patronymic }
        data["subject"] = subj.subject.name
        res.append(data)
    return Response({"status": "ok", "subjects": res})

@api_view(['GET'])
@authentication_classes([CsrfExemptSessionAuthentication])
@permission_classes([IsAuthorized, HasCourseAccess])
def courseprofile(request, course_id):
    subj = ClassSubject.objects.select_related("subject", "teacher", "school_class").get(id=course_id)

    teacher = model_to_dict(subj.teacher)
    del teacher["user"]

    teacher_subjects = ClassSubject.objects.select_related("subject", "school_class").filter(teacher=subj.teacher)

    teacherInfo = ClassSubject.objects.filter(teacher=subj.teacher).all()
    teacher["subjects"] = list(teacher_subjects.values_list("subject__name", flat=True))
    teacher["classes"] = list(teacher_subjects.values_list("school_class__name", flat=True))
    
    data = {"name": subj.subject.name, "teacher": teacher}
    return Response({"status": "ok", "profile": data})

@api_view(['GET'])
@authentication_classes([CsrfExemptSessionAuthentication])
@permission_classes([IsAuthorized, HasCourseAccess])
def courselessons(request, course_id):
    subj = ClassSubject.objects.select_related("subject", "teacher", "school_class").get(id=course_id)
    
    lessons = list(Lesson.objects.filter(class_subject=subj).values_list("id", "topic", "date"))

    return Response({"status": "ok", "lessons": lessons})

@api_view(['GET'])
@authentication_classes([CsrfExemptSessionAuthentication])
@permission_classes([IsAuthorized, HasLessonAccess])
def courselesson(request, lesson_id):
    lesson = Lesson.objects.get(id=lesson_id)
    teacher_data = model_to_dict(UserProfile.objects.get(user=lesson.class_subject.teacher.user))
    del teacher_data["user"]
    data = {
        "id": lesson.id,
        "topic": lesson.topic,
        "teacher": teacher_data,
        "date": lesson.date,
    }

    return Response({"status": "ok", "lesson": data})


from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from .serializers import CourseSerializer

class CourseViewSet(ModelViewSet):
    queryset = ClassSubject.objects.all()
    serializer_class = CourseSerializer
    authentication_classes = [CsrfExemptSessionAuthentication]

    # @action(detail=True, methods=["get"])
    # def list(self, request, *args, **kwargs):
    #     subjects = ClassSubject.objects.filter(school_class=class_id).select_related("school_class", "subject", "teacher")
    #     res = []
    #     for subj in subjects: 
    #         data = {}
    #         profile = UserProfile.objects.get(user=subj.teacher.user)
    #         data["id"] = subj.id
    #         data["teacher"] = { "user": subj.teacher.user.id,
    #                         "first_name": profile.first_name,
    #                         "last_name": profile.last_name,
    #                         "patronymic": profile.patronymic }
    #         data["subject"] = subj.subject.name
    #         res.append(data)
    #     return Response({"status": "ok", "subjects": res})