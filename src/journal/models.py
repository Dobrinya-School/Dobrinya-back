from django.db import models
from edu.models import StudentProfile, TeacherProfile

class SchoolClass(models.Model):
    name = models.CharField(max_length=20)
    year = models.PositiveSmallIntegerField(db_index=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        indexes = [
            models.Index(fields=["year"]),
        ]
        constraints = [
            models.UniqueConstraint(fields=["name", "year"], name="uniq_class_per_year")
        ]

    def __str__(self):
        return f"{self.name} ({self.year})"


class Subject(models.Model):
    name = models.CharField(max_length=100, unique=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class ClassSubject(models.Model):
    school_class = models.ForeignKey(SchoolClass, on_delete=models.CASCADE, related_name="subjects")
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    teacher = models.ForeignKey(TeacherProfile, on_delete=models.PROTECT)
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


class Enrollment(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)
    school_class = models.ForeignKey(SchoolClass, on_delete=models.CASCADE)
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


class Lesson(models.Model):
    class_subject = models.ForeignKey(ClassSubject, on_delete=models.CASCADE)
    date = models.DateField(db_index=True)
    topic = models.CharField(max_length=255, blank=True)
    homework = models.TextField(blank=True)
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


class Grade(models.Model):
    GRADE_TYPES = [
        ("lesson", "Lesson"),
        ("exam", "Exam"),
        ("homework", "Homework"),
    ]

    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name="grades")
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

    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name="attendance")
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
