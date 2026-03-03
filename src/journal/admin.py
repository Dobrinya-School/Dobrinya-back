from django.contrib import admin

from .models import *

@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ['student', 'lesson', 'value']