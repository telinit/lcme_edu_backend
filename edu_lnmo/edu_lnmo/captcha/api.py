from django.http import HttpResponse
from drf_yasg.utils import swagger_auto_schema
from rest_framework import serializers
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.serializers import Serializer
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_200_OK
from rest_framework.viewsets import ViewSet

from .captcha import Captcha
from ..activity.models import Activity
from ..course.models import Course
from ..mark.models import Mark
from ..user.auth import MultiTokenAuthentication
from ..user.models import User


class CaptchaViewSet(ViewSet):

    class ChallengeSerializer(Serializer):
        challenge = serializers.CharField()

    @swagger_auto_schema(responses={200: ChallengeSerializer()})
    @action(methods=['GET'], detail=False)
    def challenge(self, request):
        cap = Captcha()
        obj = {
            "challenge": cap.challenge
        }
        ser = __class__.ChallengeSerializer(obj)
        return Response(ser.data)

    @action(methods=['GET'], detail=True)
    def image(self, request, pk):
        try:
            cap = Captcha(pk)
        except Exception as e:
            return Response(status=HTTP_400_BAD_REQUEST)

        data = cap.generate_image()

        return HttpResponse(content=data, status=HTTP_200_OK, content_type="image/png")

    authentication_classes = []
    permission_classes = [AllowAny]