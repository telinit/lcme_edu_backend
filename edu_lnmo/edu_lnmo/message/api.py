from django.contrib.auth.models import AnonymousUser
from django.db.models import Q
from rest_framework import permissions, viewsets, serializers
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.permissions import BasePermission
from rest_framework.request import Request
from rest_framework_simplejwt.authentication import JWTAuthentication

from .models import Message, MessagePrivate, MessageTaskSubmission, MessageNews
from ..user.models import User
from ..util.rest import EduModelViewSet, EduModelSerializer, request_user_is_staff, request_user_is_authenticated


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


class MessageViewSet(EduModelViewSet):  # TODO: Secure

    class MessagePermissions(BasePermission):

        def has_permission(self, request: Request, view: "MessageViewSet"):
            if view.action == "create":
                return False
            else:
                return request_user_is_authenticated(request)

        def has_object_permission(self, request: Request, view: "MessageViewSet", obj: Message):
            if view.action in ["retrieve", "update", "partial_update", "destroy"]:
                return request_user_is_authenticated(request) and \
                       obj.sender == request.user
            else:
                return False

    def get_queryset(self):
        u: User = self.request.user

        if isinstance(u, AnonymousUser):
            return None
        elif u.is_staff or u.is_superuser:
            return Message.objects.all()
        else:
            return Message.objects.filter(sender=u)

    serializer_class = MessageSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [MessagePermissions]


class MessagePrivateViewSet(EduModelViewSet):  # TODO: Secure

    class MessagePrivatePermissions(BasePermission):

        def has_permission(self, request: Request, view: "MessagePrivateViewSet"):
            if view.action == "create":
                return "sender" in request.data and \
                       request.data["sender"] == str(request.user.id)
            else:
                return request_user_is_authenticated(request)

        def has_object_permission(self, request: Request, view: "MessagePrivateViewSet", obj: MessagePrivate):
            if view.action == "retrieve":
                return obj.sender == request.user or obj.receiver == request.user
            if view.action in ["update", "partial_update", "destroy"]:
                return obj.sender == request.user
            else:
                return False

    def get_queryset(self):
        u: User = self.request.user

        if isinstance(u, AnonymousUser):
            return None
        elif u.is_staff or u.is_superuser:
            return MessagePrivate.objects.all()
        else:
            return MessagePrivate.objects.filter(Q(sender=u) | Q(receiver=u))

    serializer_class = MessagePrivateSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [MessagePrivatePermissions]


class MessageTaskSubmissionViewSet(EduModelViewSet):  # TODO: Secure

    class MessageTaskSubmissionPermissions(BasePermission):

        def has_permission(self, request: Request, view: "MessageTaskSubmissionViewSet"):
            if view.action == "create":
                return "sender" in request.data and \
                       request.data["sender"] == str(request.user.id)
            else:
                return request_user_is_authenticated(request)

        def has_object_permission(self, request: Request, view: "MessageTaskSubmissionViewSet", obj: MessageTaskSubmission):
            if view.action == "retrieve":
                return obj.sender == request.user or obj.receiver == request.user
            if view.action in ["update", "partial_update", "destroy"]:
                return obj.sender == request.user
            else:
                return False

    def get_queryset(self):
        u: User = self.request.user

        if isinstance(u, AnonymousUser):
            return None
        elif u.is_staff or u.is_superuser:
            return MessageTaskSubmission.objects.all()
        else:
            return MessageTaskSubmission.objects.filter(Q(sender=u) | Q(receiver=u))

    serializer_class = MessageTaskSubmissionSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [MessageTaskSubmissionPermissions]


class MessageNewsViewSet(EduModelViewSet):

    class MessageNewsPermissions(BasePermission):

        def has_permission(self, request: Request, view: "MessageNewsViewSet"):
            if view.action == "create":
                return request_user_is_staff(request)
            else:
                return request_user_is_authenticated(request)

        def has_object_permission(self, request: Request, view: "MessageNewsViewSet", obj: MessageNews):
            if view.action in ["update", "partial_update", "destroy"]:
                return request_user_is_staff(request)
            else:
                return request_user_is_authenticated(request)

    queryset = MessageNews.objects.all()
    serializer_class = MessageNewsSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [MessageNewsPermissions]
