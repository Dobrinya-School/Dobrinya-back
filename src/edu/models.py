from django.db import models

from authh.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    first_name = models.CharField(max_length=20)
    last_name = models.CharField(max_length=40)
    patronymic = models.CharField(max_length=20)
    avatar_url = models.TextField(blank=True, null=True)
    timezone = models.TextField(blank=True, null=True)

    class Meta:
        # db_table = "edu.user_profiles"
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"

        # managed = False

    def __str__(self):
        return f"{self.last_name} {self.first_name}"

class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    school_name = models.TextField(blank=True, null=True)

    class Meta:
        # db_table = "edu.student_profiles"
        verbose_name = "Student Profile"
        verbose_name_plural = "Student Profiles"

        # managed = False

    def __str__(self):
        return f"{self.user} - "


class TeacherProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    subject = models.TextField(blank=True, null=True)
    school_name = models.TextField(blank=True, null=True)
    qualification = models.TextField(blank=True, null=True)

    class Meta:
        # db_table = "edu.teacher_profiles"
        verbose_name = "Teacher Profile"
        verbose_name_plural = "Teacher Profiles"

        # managed = False

    def __str__(self):
        return f"{self.user} - "