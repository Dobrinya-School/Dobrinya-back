from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from .models import LessonTest
from rest_framework.response import Response
from django.utils import timezone
from django.apps import apps

from accounts.utils import *
from accounts.permissions import *
from .models import *
from authh.authentification import CsrfExemptSessionAuthentication

ClassSubject = apps.get_model("edu", "ClassSubject")
LessonTest = apps.get_model("testing", "LessonTest")
Lesson = apps.get_model("edu", "Lesson")

@api_view(['GET'])
@authentication_classes([CsrfExemptSessionAuthentication])
@permission_classes([IsAuthorized])
def coursetests(request, course_id):
    subj = ClassSubject.objects.select_related("subject", "teacher", "school_class").get(id=course_id)
    lessons = subj.lessons.all()

    testsInfo = LessonTest.objects.select_related("lesson").filter(lesson__class_subject=subj)
    testsData = [
        {
            "id": test.id,
            "name": test.name,
            "description": test.description,
        }
        for test in testsInfo
    ]
    return Response({"status": "ok", "tests": testsData}, status=200)

@api_view(['POST'])
@authentication_classes([CsrfExemptSessionAuthentication])
@permission_classes([IsAuthorized, IsTeacherOrDirector, HasCourseAccess])
def createtest(request, course_id):
    lesson_id = request.data.get("lesson_id")
    name = request.data.get("name")
    description = request.data.get("description")

    if not (lesson_id and name and description):
        raise RPCPermissionDenied("Не указаны lesson_id, name, description")

    subj = ClassSubject.objects.select_related("subject", "teacher", "school_class").get(id=course_id)

    lesson = Lesson.objects.filter(id=lesson_id).first()
    if not lesson:
        raise RPCNotFound("Неверный id урока")

    test = LessonTest.objects.create(
        name=name,
        description=description,
        subject=lesson.class_subject.subject,
        lesson=lesson
    )

    return Response({"status": "ok", "detail": "Успешно создан тест", "data": {"id": test.id}}, status=200)

@api_view(['GET'])
@authentication_classes([CsrfExemptSessionAuthentication])
@permission_classes([IsAuthorized, HasTestAccess])
def testinfo(request, test_id):
    test = LessonTest.objects.select_related("subject", "lesson").get(id=test_id)

    questionsData = []
    for q in test.questions.all():
        data = {}
        data["id"] = q.id
        data["text"] = q.text
        answeredQuestion = QuestionAnswerResult.objects.filter(question=q)
        if answeredQuestion.exists():
            data["answered"] = True
            data["selected_answers"] = []
            aQst = answeredQuestion.first()
            for answ in aQst.selected_answers.all():
                a = {}
                a["id"] = answ.id
                a["is_correct"] = answ.is_correct
                data["selected_answers"].append(a)
            data["is_correct"] = aQst.is_correct
        data["answers"] = []
        for answ in q.answers.all():
            a = {}
            a["id"] = answ.id
            a["text"] = answ.text
            data["answers"].append(a)
        questionsData.append(data)

    return Response({"status": "ok", "test": {"id": test.id, "name": test.name, "description": test.description, "questions": questionsData}}, status=200)

@api_view(['POST'])
@authentication_classes([CsrfExemptSessionAuthentication])
@permission_classes([IsAuthorized, IsTeacherOrDirector, HasTestAccess])
def createquestion(request, test_id):
    text = request.data.get("text")
    answers_data = request.data.get("answers_data")

    if not (text and answers_data):
        raise RPCPermissionDenied("Не указаны text, answers_data")

    test = LessonTest.objects.select_related("subject", "lesson").get(id=test_id)

    question = TestQuestion.objects.create(
        test=test,
        text=text,
    )
    for answr in answers_data:
        answer = QuestionAnswer.objects.create(
            question=question,
            text=answr.get("text",""),
            is_correct=answr.get("is_correct", False),
        )

    return Response({"status": "ok", "detail": "Успешно создан вопрос"}, status=200)

@api_view(['POST'])
@authentication_classes([CsrfExemptSessionAuthentication])
@permission_classes([IsAuthorized, HasTestAccess])
def questionconfirm(request, test_id):
    question_id = request.data.get("question_id")
    answers_ids = request.data.get("answers_ids")

    if not (question_id and answers_ids):
        raise RPCPermissionDenied("Не указаны question_id, answer_id")
    
    test = LessonTest.objects.select_related("subject", "lesson").get(id=test_id)
    
    attempt, _ = TestAttempt.objects.get_or_create(
        test=test,
        user=UserProfile.objects.get(user=request.user)
    )

    try:
        question = TestQuestion.objects.get(id=question_id)
    except TestQuestion.DoesNotExist:
        raise RPCNotFound(detail="Неверный id вопроса")
    
    questionanswer = QuestionAnswerResult.objects.filter(attempt=attempt,question=question)
    if questionanswer.exists():
        # data = {}
        # data["answered"] = True
        # data["selected_answers"] = []
        # for answ in questionanswer.selected_answers:
        #     a = {}
        #     a["id"] = answ.id
        #     a["is_correct"] = answ.is_correct
        #     data["selected_answers"].append(a)
        # data["is_correct"] = questionanswer.is_correct
        return Response({"status": "error", "detail": "На вопрос уже отвечали"})

    answers = QuestionAnswer.objects.filter(
        id__in=answers_ids,
        question=question
    )

    if answers.count() != len(answers_ids):
        raise RPCPermissionDenied("Один или несколько id ответов неверны")
    
    correct_ids = set(
        QuestionAnswer.objects.filter(
            question=question,
            is_correct=True
        ).values_list("id", flat=True)
    )

    selected_ids = set(a.id for a in answers)

    is_correct = correct_ids == selected_ids

    res = QuestionAnswerResult.objects.create(
        attempt=attempt,
        question=question,
        is_correct=is_correct
    )
    res.selected_answers.set(selected_ids)

    completed = False
    if attempt.answers.count() == test.questions.count():
        completed = True
        attempt.finished_at = timezone.now()
        attempt.save()

    answered = QuestionAnswerResult.objects.filter(
        attempt=attempt
    ).count()

    total = TestQuestion.objects.filter(
        test=attempt.test
    ).count()

    return Response({"status": "ok",
                     "progress": {
                        "answered": answered,
                        "total": total,
                        "completed": completed,
                        "completed_percent": round(completed * 100),
                        "is_finished": answered == total
                    },
                    "data": {"is_correct": is_correct, "correct_answers": list(correct_ids)
                }})

@api_view(['GET'])
@authentication_classes([CsrfExemptSessionAuthentication])
@permission_classes([IsAuthorized, HasTestAccess])
def testresults(request, test_id):
    try:
        test = TestAttempt.objects.get(id=test_id)
    except TestAttempt.DoesNotExist:
        raise RPCNotFound("Прохождения теста не существует")
    
    data = {
        "started_at": test.started_at,
        "finished_at": test.finished_at,

        "total": test.answers.count(),
        "correct": test.answers.filter(is_correct=True).count(),
    }

    return Response({"status": "ok", "data": data}, status=200)


class TestViewSet(ModelViewSet):
    queryset = LessonTest.objects.all()
    authentication_classes = [CsrfExemptSessionAuthentication]
    
    def get_queryset(self):
        return LessonTest.objects.filter(
            course_id=self.kwargs["course_pk"]
        )

    def perform_create(self, serializer):
        serializer.save(
            course_id=self.kwargs["course_pk"]
        )

    def get_permissions(self):

        permission_map = {
            "create": [IsAuthorized, IsTeacherOrDirector, HasCourseAccess],
            "update": [IsAuthorized, IsTeacherOrDirector, HasTestAccess],
            "partial_update": [IsAuthorized, IsTeacherOrDirector, HasTestAccess],
            "destroy": [IsAuthorized, IsTeacherOrDirector, HasTestAccess],
            "info": [IsAuthorized, HasTestAccess],
            "results": [IsAuthorized, HasTestAccess],
            "submit": [IsAuthorized, HasTestAccess],
        }

        return [permission() for permission in permission_map.get(self.action, [IsAuthenticated])]

    @action(detail=True, methods=["get"])
    def list(self, request, pk=None):
        

    @action(detail=True, methods=["get"])
    def info(self, request, pk=None):
        test = self.get_object()

        questionsData = []
        for q in test.questions.all():
            data = {}
            data["id"] = q.id
            data["text"] = q.text
            answeredQuestion = QuestionAnswerResult.objects.filter(question=q)
            if answeredQuestion.exists():
                data["answered"] = True
                data["selected_answers"] = []
                aQst = answeredQuestion.first()
                for answ in aQst.selected_answers.all():
                    a = {}
                    a["id"] = answ.id
                    a["is_correct"] = answ.is_correct
                    data["selected_answers"].append(a)
                data["is_correct"] = aQst.is_correct
            data["answers"] = []
            for answ in q.answers.all():
                a = {}
                a["id"] = answ.id
                a["text"] = answ.text
                data["answers"].append(a)
            questionsData.append(data)

        return Response({"status": "ok", "test": {"id": test.id, "name": test.name, "description": test.description, "questions": questionsData}}, status=200)

    @action(detail=True, methods=["post"])
    def submit(self, request, pk=None):
        question_id = request.data.get("question_id")
        answers_ids = request.data.get("answers_ids")

        if not (question_id and answers_ids):
            raise RPCPermissionDenied("Не указаны question_id, answer_id")
        
        test = self.get_object()


        attempt, _ = TestAttempt.objects.get_or_create(
            test=test,
            user=UserProfile.objects.get(user=request.user)
        )

        try:
            question = TestQuestion.objects.get(id=question_id)
        except TestQuestion.DoesNotExist:
            raise RPCNotFound(detail="Неверный id вопроса")
        
        questionanswer = QuestionAnswerResult.objects.filter(attempt=attempt,question=question)
        if questionanswer.exists():
            # data = {}
            # data["answered"] = True
            # data["selected_answers"] = []
            # for answ in questionanswer.selected_answers:
            #     a = {}
            #     a["id"] = answ.id
            #     a["is_correct"] = answ.is_correct
            #     data["selected_answers"].append(a)
            # data["is_correct"] = questionanswer.is_correct
            return Response({"status": "error", "detail": "На вопрос уже отвечали"})

        answers = QuestionAnswer.objects.filter(
            id__in=answers_ids,
            question=question
        )

        if answers.count() != len(answers_ids):
            raise RPCPermissionDenied("Один или несколько id ответов неверны")
        
        correct_ids = set(
            QuestionAnswer.objects.filter(
                question=question,
                is_correct=True
            ).values_list("id", flat=True)
        )

        selected_ids = set(a.id for a in answers)

        is_correct = correct_ids == selected_ids

        res = QuestionAnswerResult.objects.create(
            attempt=attempt,
            question=question,
            is_correct=is_correct
        )
        res.selected_answers.set(selected_ids)

        completed = False
        if attempt.answers.count() == test.questions.count():
            completed = True
            attempt.finished_at = timezone.now()
            attempt.save()

        answered = QuestionAnswerResult.objects.filter(
            attempt=attempt
        ).count()

        total = TestQuestion.objects.filter(
            test=attempt.test
        ).count()

        return Response({"status": "ok",
                        "progress": {
                            "answered": answered,
                            "total": total,
                            "completed": completed,
                            "completed_percent": round(completed * 100),
                            "is_finished": answered == total
                        },
                        "data": {"is_correct": is_correct, "correct_answers": list(correct_ids)
                    }})

    @action(detail=True, methods=["get"])
    def results(self, request, pk=None):
        test = self.get_object()
        attempt = TestAttempt.objects.get(
            test=test,
            user=UserProfile.objects.get(user=request.user)
        )

        data = {
            "started_at": test.started_at,
            "finished_at": test.finished_at,

            "total": test.answers.count(),
            "correct": test.answers.filter(is_correct=True).count(),
        }

        return Response({"status": "ok", "data": data}, status=200)
