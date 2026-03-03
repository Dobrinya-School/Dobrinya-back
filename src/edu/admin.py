from django.contrib import admin

from .models import *

@admin.register(School)
class SchoolAdmin(admin.ModelAdmin):
    list_display = ['name', 'city']
    list_filter = ['city']

@admin.register(SchoolClass)
class SchoolClassAdmin(admin.ModelAdmin):
    list_display = ['name', 'year']
    list_filter = ['year']

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ['name']

@admin.register(ClassSubject)
class ClassSubjectAdmin(admin.ModelAdmin):
    list_display = ['school_class', 'subject', 'teacher']

@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ['topic', 'class_subject', 'date']
    list_filter = ['class_subject', 'date']

@admin.register(HomeWork)
class HomeWorkAdmin(admin.ModelAdmin):
    list_display = ['lesson']

@admin.register(TextHomeWork)
class TextHomeWorkAdmin(admin.ModelAdmin):
    list_display = ['homework', 'created_at']

@admin.register(FileHomeWork)
class FileHomeWorkAdmin(admin.ModelAdmin):
    list_display = ['homework', 'created_at', 'file']

@admin.register(UserHomeWork)
class UserHomeWorkAdmin(admin.ModelAdmin):
    list_display = ['user', 'homework', 'status', 'created_at']