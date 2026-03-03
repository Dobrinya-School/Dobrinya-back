from django.urls import path, include

from .views import *
from testing.views import *

urlpatterns = [
    path("profile/", profile, name="profile"),
    path("public/profile/<uuid:user_id>/", publicprofile, name="user-profile"),
    
    path("role/<uuid:user_id>/", roleprofile, name="role-profile"),

    path("cities/", cities, name="cities"),
    path("schools/", schools, name="city-schools"),
    path("school/<uuid:school_id>/", schoolprofile, name="school-profile"),
    path("classes/<uuid:school_id>/", classes, name="school-classes"),

    path("class/<uuid:class_id>/", classprofile, name="class-profile"),
    path("class/<uuid:class_id>/students/", classstudents, name="class-students"),
    path("class/<uuid:class_id>/subjects/", classsubjects, name="class-subjects"),
    path("course/<uuid:course_id>/", courseprofile, name="course-profile"),
    path("course/<uuid:course_id>/lessons/", courselessons, name="course-lessons"),
    # path("lesson/<uuid:lesson_id>/", courselesson, name="course-lesson"),
    path("lesson/<int:lesson_id>/", courselesson, name="course-lesson"),

    # path("course/<uuid:course_id>/tests/", coursetests, name="course-tests"),
    # path("test/<uuid:test_id>/", testinfo, name="test-info"),
    # path("tests/<uuid:course_id>/create/", createtest, name="create-test"),
    # path("questions/<uuid:test_id>/create/", createquestion, name="create-question"),
    # path("test/<uuid:test_id>/answer/", questionconfirm, name="question-confirm"),
    # path("test/<uuid:test_id>/results/", testresults, name="test-results"),
]

from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register("courses", CourseViewSet)

urlpatterns += router.urls