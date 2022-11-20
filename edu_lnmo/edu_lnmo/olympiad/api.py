import uuid

from django.contrib.auth.models import AnonymousUser
from django.db.models import QuerySet, Q
from rest_framework import viewsets, serializers, permissions
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import BasePermission
from rest_framework.request import Request

from .models import Activity, Olympiad, OlympiadParticipation
from ..course.models import Course, CourseEnrollment
from ..user.auth import MultiTokenAuthentication
from ..user.models import User
from ..util.rest import request_user_is_staff, EduModelViewSet, request_user_is_authenticated, EduModelSerializer, \
    EduModelReadSerializer


class OlympiadSerializer(EduModelSerializer):
    class Meta(EduModelSerializer.Meta):
        model = Olympiad
        fields = '__all__'


class OlympiadViewSet(EduModelViewSet):
    class OlympiadPermissions(BasePermission):
        def has_permission(self, request: Request, view: "OlympiadViewSet"):
                return request_user_is_authenticated(request)

        def has_object_permission(self, request: Request, view: "OlympiadViewSet", obj: Olympiad):
            if view.action in ["update", "partial_update", "destroy"]:
                return request_user_is_staff(request)
            else:
                return request_user_is_authenticated(request)

    def get_queryset(self):
        u: User = self.request.user

        if isinstance(u, AnonymousUser):
            return None
        else:
            return Olympiad.objects.all()

    serializer_class = OlympiadSerializer
    authentication_classes = [MultiTokenAuthentication]
    permission_classes = [OlympiadPermissions]
    filterset_fields = ['name', 'category', 'website', 'location', 'department__organization__name', 'department__name']
    search_fields = ['name', 'category', 'website', 'location', 'department__organization__name', 'department__name']


class OlympiadParticipationSerializer(EduModelSerializer):
    class Meta(EduModelSerializer.Meta):
        model = Olympiad
        fields = '__all__'


class OlympiadParticipationViewSet(EduModelViewSet):
    class OlympiadParticipationPermissions(BasePermission):
        def has_permission(self, request: Request, view: "OlympiadParticipationViewSet"):
                return request_user_is_authenticated(request)

        def has_object_permission(self, request: Request, view: "OlympiadParticipationViewSet", obj: OlympiadParticipation):
            if view.action in ["update", "partial_update", "destroy"]:
                return request_user_is_staff(request) or \
                    obj.person.id in ([request.user.id] + request.user.children)
            else:
                return request_user_is_authenticated(request)

    def get_queryset(self):
        u: User = self.request.user

        if isinstance(u, AnonymousUser):
            return None
        else:
            return OlympiadParticipation.objects.all()

    serializer_class = OlympiadParticipationSerializer
    authentication_classes = [MultiTokenAuthentication]
    permission_classes = [OlympiadParticipationPermissions]
    filterset_fields = ['date', 'olympiad__id', 'person__id', 'date', 'award', 'team_member']
    search_fields = ['date', 'award']
