from django.contrib import admin

from .models import *

@admin.register(StudentProfile, TeacherProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'school_name']
    list_filter = ['school_name']