from rest_framework import permissions, viewsets, serializers
from rest_framework.authentication import SessionAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication

from .models import File
from ..util.rest import EduModelViewSet, EduModelSerializer


class FileSerializer(EduModelSerializer):
    class Meta(EduModelSerializer.Meta):
        model = File
        fields = '__all__'


class FileViewSet(EduModelViewSet):
    queryset = File.objects.all()
    serializer_class = FileSerializer
    authentication_classes = [SessionAuthentication]
    permission_classes = []
