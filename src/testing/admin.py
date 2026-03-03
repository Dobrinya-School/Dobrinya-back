from django.contrib import admin

from .models import *

@admin.register(LessonTest)
class LessonTestAdmin(admin.ModelAdmin):
    list_display = ['name', 'subject', 'lesson']
    list_filter = ['subject']

@admin.register(TestQuestion)
class TestQuestionAdmin(admin.ModelAdmin):
    list_display = ['test', 'text']
    list_filter = ['test']

@admin.register(QuestionAnswer)
class QuestionAnswerAdmin(admin.ModelAdmin):
    list_display = ['question', 'text', 'is_correct']
    list_filter = ['question', 'is_correct']

@admin.register(TestAttempt)
class TestAttemptAdmin(admin.ModelAdmin):
    list_display = ['test', 'user', 'started_at', 'finished_at']

@admin.register(QuestionAnswerResult)
class QuestionAnswerResultAdmin(admin.ModelAdmin):
    list_display = ['attempt', 'question', 'is_correct']