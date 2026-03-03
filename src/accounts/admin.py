from django.contrib import admin

from .models import *

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['last_name', 'first_name', 'patronymic', 'user']
    list_filter = ['last_name', 'first_name', 'patronymic']

@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'school_class']
    list_filter = ['school_class']

@admin.register(TeacherProfile)
class TeacherProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'school']
    list_filter = ['school']
