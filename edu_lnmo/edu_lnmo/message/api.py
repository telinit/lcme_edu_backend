from django.contrib.auth.models import AnonymousUser
from django.db.models import Q
from rest_framework import permissions, viewsets, serializers
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import BasePermission
from rest_framework.request import Request
from rest_framework_simplejwt.authentication import JWTAuthentication

from .models import Message, MessageThread
from ..activity.models import Activity
from ..user.auth import MultiTokenAuthentication
from ..user.models import User
from ..util.rest import EduModelViewSet, EduModelSerializer, request_user_is_staff, request_user_is_authenticated


class MessageSerializer(EduModelSerializer):
    class Meta(EduModelSerializer.Meta):
        model = Message
        fields = '__all__'


class MessageThreadSerializer(EduModelSerializer):
    class Meta(EduModelSerializer.Meta):
        model = MessageThread
        fields = '__all__'


class MessageViewSet(EduModelViewSet):  # TODO: Secure

    class MessagePermissions(BasePermission):

        def has_permission(self, request: Request, view: "MessageViewSet"):
            if view.action == "create":
                data = request.data
                if data["type"] in [Message.MessageType.NEW, Message.MessageType.MAN]:
                    return request_user_is_staff(request)
                elif data["type"] == Message.MessageType.PRV:
                    return True
                elif data["type"] == Message.MessageType.THR:
                    thread = MessageThread.objects.filter(data['thread'])
                    return thread and (
                            thread[0].members.filter(id=request.user.id) or
                            request_user_is_staff(request)
                    )
                else:
                    return False
            else:
                return request_user_is_authenticated(request)

        def has_object_permission(self, request: Request, view: "MessageViewSet", obj: Message):
            if view.action in ["retrieve", "update", "partial_update", "destroy"]:
                if not request_user_is_authenticated(request):
                    return False
                else:
                    is_sender = obj.sender.id == request.user.id
                    is_receiver = obj.receiver.id == request.user.id
                    is_thread_member = request.user in obj.thread.members if obj.thread else False
                    return is_sender or is_receiver or is_thread_member or \
                           request_user_is_staff(request)
            else:
                return False

    def get_queryset(self):
        u: User = self.request.user

        if isinstance(u, AnonymousUser):
            return None
        elif u.is_staff or u.is_superuser:
            return Message.objects.all()
        else:
            return Message.objects.filter(Q(sender=u) | Q(receiver=u) | Q(thread__members__in=u))

    serializer_class = MessageSerializer
    authentication_classes = [MultiTokenAuthentication]
    permission_classes = [MessagePermissions]


class MessageThreadViewSet(EduModelViewSet):

    class MessageThreadPermissions(BasePermission):

        def has_permission(self, request: Request, view: "MessageThreadViewSet"):
            if view.action == "create":
                t = request.data['type']
                if not t:
                    return False
                else:
                    if t in [MessageThread.ThreadType.GRP, MessageThread.ThreadType.SUP]:
                        return True
                    elif t == MessageThread.ThreadType.FRM:
                        return True
                    else:
                        return False

            else:
                return request_user_is_authenticated(request)

        def has_object_permission(self, request: Request, view: "MessageThreadViewSet", obj: MessageThread):
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

    serializer_class = MessageThreadSerializer
    authentication_classes = [MultiTokenAuthentication]
    permission_classes = [MessageThreadPermissions]