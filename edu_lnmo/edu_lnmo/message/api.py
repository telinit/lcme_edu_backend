from rest_framework import permissions, viewsets, serializers
from rest_framework_simplejwt.authentication import JWTAuthentication

from .models import Message, MessagePrivate, MessageTaskSubmission, MessageNews


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = '__all__'


class MessagePrivateSerializer(serializers.ModelSerializer):
    class Meta:
        model = MessagePrivate
        fields = '__all__'


class MessageTaskSubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = MessageTaskSubmission
        fields = '__all__'


class MessageNewsSerializer(serializers.ModelSerializer):
    class Meta:
        model = MessageNews
        fields = '__all__'


class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.AllowAny]


class MessagePrivateViewSet(viewsets.ModelViewSet):
    queryset = MessagePrivate.objects.all()
    serializer_class = MessagePrivateSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.AllowAny]


class MessageTaskSubmissionViewSet(viewsets.ModelViewSet):
    queryset = MessageTaskSubmission.objects.all()
    serializer_class = MessageTaskSubmissionSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.AllowAny]


class MessageNewsViewSet(viewsets.ModelViewSet):
    queryset = MessageNews.objects.all()
    serializer_class = MessageNewsSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.AllowAny]