from rest_framework import serializers
from .models import ClassSubject

class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassSubject
        fields = "__all__"