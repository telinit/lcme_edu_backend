from django.contrib.auth.models import AnonymousUser
from rest_framework import viewsets, serializers, permissions
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import BasePermission
from rest_framework.request import Request
from rest_framework_simplejwt.authentication import JWTAuthentication

from .models import UnreadObject
from ..user.auth import MultiTokenAuthentication
from ..user.models import User
from ..util.rest import EduModelViewSet, EduModelSerializer, request_user_is_staff, request_user_is_authenticated


class UnreadObjectSerializer(EduModelSerializer):
    class Meta(EduModelSerializer.Meta):
        model = UnreadObject
        fields = '__all__'


class UnreadObjectViewSet(EduModelViewSet):
    class UnreadObjectPermissions(BasePermission):

        def has_permission(self, request: Request, view: "UnreadObjectViewSet"):
            if view.action == "create":
                return False  # TODO: Remove this action entirely
            else:
                return request_user_is_authenticated(request)

        def has_object_permission(self, request: Request, view: "UnreadObjectViewSet", obj: UnreadObject):
            if view.action in ["update", "partial_update"]:
                return False  # TODO: Remove these actions entirely
            elif view.action in ["destroy", "retrieve"]:
                return obj.user == request.user
            else:
                return False

    def get_queryset(self):
        u: User = self.request.user

        if isinstance(u, AnonymousUser):
            return None
        else:
            return UnreadObject.objects.filter(user=u)

    serializer_class = UnreadObjectSerializer
    authentication_classes = [MultiTokenAuthentication]
    permission_classes = [UnreadObjectPermissions]
