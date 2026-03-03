from django.urls import path, include

from .views import *

# urlpatterns = [
#     path("course/<uuid:course_id>/tests/", coursetests, name="course-tests"),
#     path("<uuid:test_id>/", testinfo, name="test-info"),
#     path("<uuid:course_id>/create/", createtest, name="test-create"),
#     path("<uuid:course_id>/edit/", createtest, name="test-edit"),
#     path("<uuid:course_id>/delete/", createtest, name="test-delete"),
#     path("questions/<uuid:test_id>/create/", createquestion, name="question-create"),
#     path("questions/<uuid:test_id>/edit/", createquestion, name="question-edit"),
#     path("questions/<uuid:test_id>/delete/", createquestion, name="question-delete"),
#     path("test/<uuid:test_id>/submit/", questionconfirm, name="question-submit"),
#     path("test/<uuid:test_id>/results/", testresults, name="test-results"),
# ]

from rest_framework.routers import DefaultRouter
from rest_framework_nested.routers import NestedDefaultRouter
from .views import *

from edu.urls import router

courses_router = NestedDefaultRouter(router, "courses", lookup="course")
courses_router.register("tests", TestViewSet, basename="course-tests")

urlpatterns = router.urls + courses_router.urls