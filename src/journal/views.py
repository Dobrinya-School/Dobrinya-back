from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework import status
from django.forms.models import model_to_dict
from django.apps import apps

from accounts.utils import *
from accounts.permissions import *
from authh.authentification import CsrfExemptSessionAuthentication
from .models import *

@api_view(["GET"])
@authentication_classes([CsrfExemptSessionAuthentication])
@permission_classes([IsAuthorized])
def classjournal(request):
    pass