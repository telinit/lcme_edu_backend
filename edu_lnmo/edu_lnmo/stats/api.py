from drf_yasg.utils import swagger_auto_schema
from rest_framework import serializers
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.serializers import Serializer
from rest_framework.viewsets import ViewSet

from ..activity.models import Activity
from ..course.models import Course
from ..mark.models import Mark
from ..user.models import User


class StatsViewSet(ViewSet):

    class CountersSerializer(Serializer):
        courses = serializers.IntegerField()
        users = serializers.IntegerField()
        activities = serializers.IntegerField()
        marks = serializers.IntegerField()

    @swagger_auto_schema(responses={200: CountersSerializer()})
    @action(methods=['GET'], detail=False)
    def counters(self, blah):
        obj = {
            "courses": Course.objects.count(),
            "users": User.objects.count(),
            "activities": Activity.objects.count(),
            "marks": Mark.objects.count(),
        }
        ser = __class__.CountersSerializer(obj)
        return Response(ser.data)

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]