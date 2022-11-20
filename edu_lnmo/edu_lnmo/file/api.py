from django.contrib.auth.models import AnonymousUser
from django.db.models import Q
from rest_framework import permissions, viewsets, serializers
from rest_framework.authentication import SessionAuthentication
from rest_framework.fields import SerializerMethodField
from rest_framework.permissions import BasePermission
from rest_framework.request import Request
from rest_framework.reverse import reverse
from rest_framework_simplejwt.authentication import JWTAuthentication

from .models import File
from ..user.auth import MultiTokenAuthentication
from ..user.models import User
from ..util.rest import EduModelViewSet, EduModelSerializer, request_user_is_staff, request_user_is_authenticated


class FileSerializer(EduModelSerializer):

    download_url = SerializerMethodField("get_download_url", read_only=True)

    def get_download_url(self):
        return f"/api/file/{self.id}/download"

    class Meta(EduModelSerializer.Meta):
        model = File
        fields = '__all__'


class FileViewSet(EduModelViewSet):

    class FilePermissions(BasePermission):

        def has_permission(self, request: Request, view: "FileViewSet"):
            if view.action == "create":
                return request_user_is_staff(request)
            else:
                return request_user_is_authenticated(request)

        def has_object_permission(self, request: Request, view: "FileViewSet", obj: File):
            if view.action in ["update", "partial_update", "destroy"]:
                return request_user_is_staff(request)
            else:
                return request_user_is_authenticated(request)

    def get_queryset(self):
        u: User = self.request.user

        if isinstance(u, AnonymousUser):
            return None
        elif u.is_staff or u.is_superuser:
            return File.objects.all()
        else:
            users = User.objects.filter(id=u.id) | u.children.all()
            # users = [*users.all()]
            q1 = Q(messages__sender__in=users)
            q2 = Q(messages__messageprivate__receiver__in=users)
            q3 = Q(course_covers__enrollments__person__in=users)
            q4 = Q(course_logos__enrollments__person__in=users)
            q5 = Q(activities__course__enrollments__person__in=users)
            return File.objects.filter(q1 | q2 | q3 | q4 | q5)

    serializer_class = FileSerializer
    authentication_classes = [MultiTokenAuthentication]
    permission_classes = [FilePermissions]
