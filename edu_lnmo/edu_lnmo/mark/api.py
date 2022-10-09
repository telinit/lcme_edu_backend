from rest_framework import permissions, viewsets, serializers
from rest_framework.authentication import SessionAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication

from .models import Mark
from ..util.rest import EduModelViewSet, EduModelSerializer


class MarkSerializer(EduModelSerializer):
    class Meta(EduModelSerializer.Meta):
        model = Mark
        fields = '__all__'


class MarkViewSet(EduModelViewSet):
    queryset = Mark.objects.all()
    serializer_class = MarkSerializer
    authentication_classes = [SessionAuthentication]
    permission_classes = []