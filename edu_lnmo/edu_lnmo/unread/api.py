from rest_framework import viewsets, serializers, permissions
from rest_framework.authentication import SessionAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication

from .models import UnreadObject
from ..util.rest import EduModelViewSet, EduModelSerializer


class UnreadObjectSerializer(EduModelSerializer):
    class Meta(EduModelSerializer.Meta):
        model = UnreadObject
        fields = '__all__'


class UnreadObjectViewSet(EduModelViewSet):
    queryset = UnreadObject.objects.all()
    serializer_class = UnreadObjectSerializer
    authentication_classes = [SessionAuthentication]
    permission_classes = []
