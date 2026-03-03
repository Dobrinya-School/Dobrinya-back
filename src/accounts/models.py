from django.contrib.auth.models import Group
from django.db import models

class UserProfile(models.Model):
    user = models.OneToOneField('authh.User', on_delete=models.CASCADE, primary_key=True)
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
    user = models.OneToOneField('authh.User', on_delete=models.CASCADE, primary_key=True)
    school_class = models.ForeignKey(
        'edu.SchoolClass',
        on_delete=models.SET_NULL,
        null=True,
        related_name='students'
    )

    class Meta:
        # db_table = "edu.student_profiles"
        verbose_name = "Student Profile"
        verbose_name_plural = "Student Profiles"

        # managed = False

    def __str__(self):
        return f"{self.user} - "
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        group, _ = Group.objects.get_or_create(name="students")
        self.user.groups.add(group)

class TeacherProfile(models.Model):
    user = models.OneToOneField('authh.User', on_delete=models.CASCADE, primary_key=True)
    subjects = models.TextField(blank=True, null=True)
    school = models.ForeignKey('edu.School', on_delete=models.CASCADE, related_name="teachers", null=True, blank=True)
    # qualifications = models.TextField(blank=True, null=True)

    class Meta:
        # db_table = "edu.teacher_profiles"
        verbose_name = "Teacher Profile"
        verbose_name_plural = "Teacher Profiles"

        # managed = False

    def __str__(self):
        return f"{self.user} - "
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        group, _ = Group.objects.get_or_create(name="teachers")
        self.user.groups.add(group)

class ParentProfile(models.Model):
    user = models.OneToOneField('authh.User', on_delete=models.CASCADE, primary_key=True)
    student = models.OneToOneField('accounts.StudentProfile', on_delete=models.CASCADE)

    class Meta:
        # db_table = "edu.student_profiles"
        verbose_name = "Parent Profile"
        verbose_name_plural = "Parent Profiles"

        # managed = False

    def __str__(self):
        return f"{self.user} - "

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        group, _ = Group.objects.get_or_create(name="parents")
        self.user.groups.add(group)