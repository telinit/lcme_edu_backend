from rest_framework import permissions, viewsets, serializers
from rest_framework.authentication import SessionAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication

from .models import Message, MessagePrivate, MessageTaskSubmission, MessageNews
from ..util.rest import EduModelViewSet, EduModelSerializer


class MessageSerializer(EduModelSerializer):
    class Meta(EduModelSerializer.Meta):
        model = Message
        fields = '__all__'


class MessagePrivateSerializer(EduModelSerializer):
    class Meta(EduModelSerializer.Meta):
        model = MessagePrivate
        fields = '__all__'


class MessageTaskSubmissionSerializer(EduModelSerializer):
    class Meta(EduModelSerializer.Meta):
        model = MessageTaskSubmission
        fields = '__all__'


class MessageNewsSerializer(EduModelSerializer):
    class Meta(EduModelSerializer.Meta):
        model = MessageNews
        fields = '__all__'


class MessageViewSet(EduModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    authentication_classes = [SessionAuthentication]
    permission_classes = []


class MessagePrivateViewSet(EduModelViewSet):
    queryset = MessagePrivate.objects.all()
    serializer_class = MessagePrivateSerializer
    authentication_classes = [SessionAuthentication]
    permission_classes = []


class MessageTaskSubmissionViewSet(EduModelViewSet):
    queryset = MessageTaskSubmission.objects.all()
    serializer_class = MessageTaskSubmissionSerializer
    authentication_classes = [SessionAuthentication]
    permission_classes = []


class MessageNewsViewSet(EduModelViewSet):
    queryset = MessageNews.objects.all()
    serializer_class = MessageNewsSerializer
    authentication_classes = [SessionAuthentication]
    permission_classes = []