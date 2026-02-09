from django.contrib import admin

from .models import User, UserLoginAttempt

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['email','created_at', 'is_verified', 'is_active', 'is_staff']
    list_filter = ['created_at', 'is_verified', 'is_active', 'is_staff']
    list_editable = ['is_verified', 'is_active']

@admin.register(UserLoginAttempt)
class UserLoginAttemptAdmin(admin.ModelAdmin):
    list_display = ['user', 'timestamp', 'successful', 'reason']
    list_filter = ['user', 'ip_address', 'successful', 'reason']