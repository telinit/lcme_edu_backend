from rest_framework import serializers, viewsets, permissions
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.fields import IntegerField, CharField
from rest_framework.permissions import BasePermission
from rest_framework.request import Request
from rest_framework.serializers import Serializer
from rest_framework_simplejwt.authentication import JWTAuthentication

from .models import Organization, Department
from ..util.rest import EduModelViewSet, EduModelSerializer, request_user_is_staff, request_user_is_authenticated


class ErrorMessageSerializer(Serializer):
    code = IntegerField()
    message = CharField()


class OrganizationSerializer(EduModelSerializer):
    class Meta(EduModelSerializer.Meta):
        model = Organization
        fields = '__all__'


class DepartmentSerializer(EduModelSerializer):
    organization = OrganizationSerializer()
    class Meta(EduModelSerializer.Meta):
        model = Department
        fields = '__all__'


class OrganizationViewSet(EduModelViewSet):

    class OrganizationPermissions(BasePermission):

        def has_permission(self, request: Request, view: "OrganizationViewSet"):
            if view.action == "create":
                return request_user_is_staff(request)
            else:
                return request_user_is_authenticated(request)

        def has_object_permission(self, request: Request, view: "OrganizationViewSet", obj: Organization):
            if view.action in ["update", "partial_update", "destroy"]:
                return request_user_is_staff(request)
            else:
                return request_user_is_authenticated(request)

    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [OrganizationPermissions]


class DepartmentViewSet(EduModelViewSet):
    class DepartmentPermissions(BasePermission):

        def has_permission(self, request: Request, view: "DepartmentViewSet"):
            if view.action == "create":
                return request_user_is_staff(request)
            else:
                return request_user_is_authenticated(request)

        def has_object_permission(self, request: Request, view: "DepartmentViewSet", obj: Department):
            if view.action in ["update", "partial_update", "destroy"]:
                return request_user_is_staff(request)
            else:
                return request_user_is_authenticated(request)

    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [DepartmentPermissions]