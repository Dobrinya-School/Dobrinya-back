from django.views import View
from django.http import JsonResponse
from django.core import serializers

from .models import StudentProfile

class StudentsView(View):
    def get(self, request, *args, **kwargs):
        return JsonResponse(serializers.serialize('json', StudentProfile.objects.all()), safe=False)
    