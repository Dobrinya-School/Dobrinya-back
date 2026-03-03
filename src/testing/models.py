from django.db import models
import uuid

class LessonTest(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=60)
    description = models.CharField(max_length=60, default="")
    subject = models.ForeignKey('edu.Subject', on_delete=models.CASCADE)
    lesson = models.ForeignKey('edu.Lesson', on_delete=models.CASCADE, related_name="tests")

    def __str__(self) -> str:
        return self.name

class TestQuestion(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    text = models.CharField()
    test = models.ForeignKey(LessonTest, on_delete=models.CASCADE, related_name="questions")

    def __str__(self) -> str:
        return self.text

class QuestionAnswer(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    text = models.CharField(max_length=100)
    question = models.ForeignKey(TestQuestion, on_delete=models.CASCADE, related_name="answers")    
    is_correct = models.BooleanField(default=False)

    def __str__(self) -> str:
        return self.text

class TestAttempt(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    test = models.ForeignKey(LessonTest, on_delete=models.CASCADE)
    user = models.ForeignKey("accounts.UserProfile", on_delete=models.CASCADE)
    started_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        indexes = [
            models.Index(fields=["test", "user"])
        ]

    def __str__(self) -> str:
        return f"{self.user} - {self.test}"

class QuestionAnswerResult(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    attempt = models.ForeignKey(
        TestAttempt,
        on_delete=models.CASCADE,
        related_name="answers"
    )
    question = models.ForeignKey(TestQuestion, on_delete=models.CASCADE)
    selected_answers = models.ManyToManyField(
        QuestionAnswer,
    )

    is_correct = models.BooleanField()

    class Meta:
        unique_together = ("attempt", "question")

    def __str__(self) -> str:
        return self.question.text

