from rest_framework import serializers
from .models import LessonTest

class TestSerializer(serializers.ModelSerializer):
    class Meta:
        model = LessonTest
        fields = "__all__"