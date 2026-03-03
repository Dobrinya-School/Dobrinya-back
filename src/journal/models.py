from django.db import models
import uuid

class Enrollment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey('accounts.StudentProfile', on_delete=models.CASCADE)
    school_class = models.ForeignKey('edu.SchoolClass', on_delete=models.CASCADE)
    date_from = models.DateField(db_index=True)
    date_to = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        indexes = [
            models.Index(fields=["school_class", "is_active"]),
            models.Index(fields=["student", "is_active"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["student", "school_class", "date_from"],
                name="uniq_enrollment_period"
            )
        ]

class Grade(models.Model):
    GRADE_TYPES = [
        ("lesson", "Lesson"),
        ("exam", "Exam"),
        ("homework", "Homework"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey('accounts.StudentProfile', on_delete=models.CASCADE)
    lesson = models.ForeignKey('edu.Lesson', on_delete=models.CASCADE, related_name="grades")
    value = models.PositiveSmallIntegerField()
    grade_type = models.CharField(max_length=20, choices=GRADE_TYPES, default="lesson")
    comment = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["student"]),
            models.Index(fields=["lesson"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["student", "lesson", "grade_type"],
                name="uniq_grade_per_lesson_type"
            )
        ]


class Attendance(models.Model):
    STATUS_CHOICES = [
        ("present", "Present"),
        ("absent", "Absent"),
        ("late", "Late"),
        ("excused", "Excused"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey('accounts.StudentProfile', on_delete=models.CASCADE)
    lesson = models.ForeignKey('edu.Lesson', on_delete=models.CASCADE, related_name="attendance")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    comment = models.CharField(max_length=255, blank=True)
    marked_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["student"]),
            models.Index(fields=["lesson"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["student", "lesson"],
                name="uniq_attendance_per_lesson"
            )
        ]
