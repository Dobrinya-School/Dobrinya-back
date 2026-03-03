from django.db import models
from django.utils.translation import gettext_lazy as _
import uuid

from authh.models import User

class School(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50, unique=True)
    city = models.CharField(max_length=40)

    def __str__(self):
        return f"{self.name} ({self.city})"


class SchoolClass(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=20)
    year = models.PositiveSmallIntegerField(db_index=True)

    school = models.ForeignKey(
        School,
        on_delete=models.CASCADE,
        related_name="classes"
    )

    is_active = models.BooleanField(default=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["school", "name", "year"],
                name="uniq_class_per_school_year"
            )
        ]

    def __str__(self):
        return f"{self.name} ({self.year})"


class Subject(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class ClassSubject(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school_class = models.ForeignKey(SchoolClass, on_delete=models.CASCADE, related_name="subjects")
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    teacher = models.ForeignKey('accounts.TeacherProfile', on_delete=models.PROTECT, related_name="classes")
    is_active = models.BooleanField(default=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["school_class", "subject"],
                name="uniq_subject_per_class"
            )
        ]

    def __str__(self):
        return f"{self.school_class} — {self.subject}"

class Lesson(models.Model):
    # КРЧ ЭТО НАДО БУДЕТ ФИКСИТЬ

    # id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    class_subject = models.ForeignKey('edu.ClassSubject', on_delete=models.CASCADE, related_name="lessons")
    date = models.DateField(db_index=True)
    topic = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["class_subject", "date"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["class_subject", "date"],
                name="uniq_lesson_per_day"
            )
        ]

    def __str__(self):
        return f"{self.class_subject} — {self.date}"

class HomeWork(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    lesson = models.ForeignKey('edu.Lesson', on_delete=models.CASCADE, related_name="homework")

    def __str__(self) -> str:
        return f"{str(self.lesson)} - Homework"

class TextHomeWork(models.Model):
    homework = models.ForeignKey('edu.HomeWork', on_delete=models.CASCADE, related_name="textHomeWork", primary_key=True)
    text=models.CharField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{str(self.homework)} - Text"
    
class FileHomeWork(models.Model):
    homework = models.ForeignKey('edu.HomeWork', on_delete=models.CASCADE, related_name="fileHomeWork", primary_key=True)
    text=models.CharField(blank=True)
    file = models.URLField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{str(self.homework)} - File"

class UserHomeWork(models.Model):

    class HomeWorkStatus(models.TextChoices):
        DONE = "DN", _("Проверено")
        ON_CHECK = "CH", _("На проверке")
        WAITING = "WN", _("Ожидает проверки")

    user = models.ForeignKey('accounts.UserProfile', on_delete=models.CASCADE, related_name="homeworks")
    homework = models.ForeignKey('edu.HomeWork', on_delete=models.CASCADE, primary_key=True)

    text=models.CharField(blank=True)
    file = models.URLField()
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=3,
        choices=HomeWorkStatus.choices,
        default=HomeWorkStatus.WAITING,
    )

