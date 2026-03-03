from rest_framework.permissions import BasePermission
from django.apps import apps

from .exceptions import *

UserProfile = apps.get_model("accounts", "UserProfile")
StudentProfile = apps.get_model("accounts", "StudentProfile")
TeacherProfile = apps.get_model("accounts", "TeacherProfile")
SchoolClass = apps.get_model("edu", "SchoolClass")
ClassSubject = apps.get_model("edu", "ClassSubject")
LessonTest = apps.get_model("testing", "LessonTest")
Lesson = apps.get_model("edu", "Lesson")

class IsAuthorized(BasePermission):
    def has_permission(self, request, view):
        if not bool(request.user and request.user.is_authenticated):
            raise RPCPermissionDenied(detail="Пользователь не авторизован")
        return True

class IsTeacher(BasePermission):
    def has_permission(self, request, view):
        if not request.user.groups.filter(name="teachers").exists():
            raise RPCPermissionDenied(detail="Пользователь не учитель")
        return True

class IsTeacherOrDirector(BasePermission):
    def has_permission(self, request, view):
        if not request.user.groups.filter(name__in=["teachers", "directors"]).exists():
            raise RPCPermissionDenied(detail="Пользователь не учитель или директор")

class HasRole(BasePermission):
    def has_permission(self, request, view):
        if not request.user.groups.filter(name__in=["teachers", "students", "directors"]).exists():
            raise RPCPermissionDenied()
        return True

class HasClassAccess(BasePermission):
    def has_permission(self, request, view):
        user = request.user

        class_id = view.kwargs.get("class_id")
        if not class_id:
            raise RPCNotFound(detail="class_id не найден")
        
        try:
            obj = SchoolClass.objects.get(id=class_id)
        except SchoolClass.DoesNotExist:
            raise RPCNotFound(detail="Класс не найден")

        if user.groups.filter(name="directors").exists():
            try:
                teacher_profile = TeacherProfile.objects.get(user=user)
            except TeacherProfile.DoesNotExist:
                raise RPCPermissionDenied()
            if not teacher_profile.school == obj.school:
                raise RPCPermissionDenied()
            return True
        
        if user.groups.filter(name="teachers").exists():
            try:
                teacher_profile = TeacherProfile.objects.get(user=user)
            except TeacherProfile.DoesNotExist:
                raise RPCPermissionDenied()
            if not teacher_profile.school == obj.school:
                raise RPCPermissionDenied()
            return True

        if user.groups.filter(name="students").exists():
            try:
                student_profile = StudentProfile.objects.get(user=user)
            except StudentProfile.DoesNotExist:
                raise RPCPermissionDenied()
            if not obj.id == student_profile.school_class.id:
                raise RPCPermissionDenied()
            return True
        
        raise RPCPermissionDenied()

class HasCourseAccess(BasePermission):
    def checkPermission(user, course_id):
        try:
            subj = ClassSubject.objects.get(id=course_id)
        except ClassSubject.DoesNotExist:
            raise RPCNotFound(detail="Нет такого курса/предмета")
        obj = subj.school_class

        if user.groups.filter(name="directors").exists():
            try:
                teacher_profile = TeacherProfile.objects.get(user=user)
            except TeacherProfile.DoesNotExist:
                raise RPCPermissionDenied()
            if not teacher_profile.school == obj.school:
                raise RPCPermissionDenied()
            return True
        
        if user.groups.filter(name="teachers").exists():
            try:
                teacher_profile = TeacherProfile.objects.get(user=user)
            except TeacherProfile.DoesNotExist:
                raise RPCPermissionDenied()
            if not teacher_profile.school == obj.school:
                raise RPCPermissionDenied()
            return True

        if user.groups.filter(name="students").exists():
            try:
                student_profile = StudentProfile.objects.get(user=user)
            except StudentProfile.DoesNotExist:
                raise RPCPermissionDenied()
            if not obj.id == student_profile.school_class.id:
                raise RPCPermissionDenied()
            return True
        raise RPCPermissionDenied()
    def has_permission(self, request, view):
        user = request.user
        course_id = view.kwargs.get("course_id")
        if not course_id:
            raise RPCNotFound(detail="course_id не найден")
        return HasCourseAccess.checkPermission(user, course_id)

class HasTestAccess(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        test_id = view.kwargs.get("test_id")
        if not test_id:
            raise RPCNotFound(detail="test_id не найден")

        try:
            test = LessonTest.objects.get(id=test_id)
        except LessonTest.DoesNotExist:
            raise RPCNotFound(detail="Нет такого теста")
        obj = test.lesson.class_subject.school_class

        if user.groups.filter(name="directors").exists():
            try:
                teacher_profile = TeacherProfile.objects.get(user=user)
            except TeacherProfile.DoesNotExist:
                raise RPCPermissionDenied()
            if not teacher_profile.school == obj.school:
                raise RPCPermissionDenied()
            return True
        
        if user.groups.filter(name="teachers").exists():
            try:
                teacher_profile = TeacherProfile.objects.get(user=user)
            except TeacherProfile.DoesNotExist:
                raise RPCPermissionDenied()
            if not teacher_profile.school == obj.school:
                raise RPCPermissionDenied()
            return True

        if user.groups.filter(name="students").exists():
            try:
                student_profile = StudentProfile.objects.get(user=user)
            except StudentProfile.DoesNotExist:
                raise RPCPermissionDenied()
            if not obj.id == student_profile.school_class.id:
                raise RPCPermissionDenied()
            return True
        
        raise RPCPermissionDenied()

class HasLessonAccess(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        lesson_id = view.kwargs.get("lesson_id")
        if not lesson_id:
            raise RPCNotFound("lesson_id не найден")
        
        try:
            lesson = Lesson.objects.get(id=lesson_id)
        except:
            raise RPCNotFound("Урок не найден")

        return HasCourseAccess.checkPermission(user, lesson.class_subject.id)