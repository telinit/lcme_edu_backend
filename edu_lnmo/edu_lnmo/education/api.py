from django.contrib.auth.models import AnonymousUser
from rest_framework import permissions, serializers, viewsets
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import BasePermission
from rest_framework.request import Request
from rest_framework_simplejwt.authentication import JWTAuthentication

from .models import Education, EducationSpecialization
from ..common.api import DepartmentSerializer
from ..user.auth import MultiTokenAuthentication
from ..user.models import User
from ..util.rest import EduModelViewSet, EduModelSerializer, request_user_is_staff, request_user_is_authenticated


class EducationSpecializationSerializer(EduModelSerializer):
    department = DepartmentSerializer()
    class Meta(EduModelSerializer.Meta):
        model = EducationSpecialization
        fields = '__all__'


class EducationShallowSerializer(EduModelSerializer):
    specialization = EducationSpecializationSerializer()

    class Meta(EduModelSerializer.Meta):
        model = Education
        fields = '__all__'


class EducationDeepSerializer(EduModelSerializer):
    specialization = EducationSpecializationSerializer()
    class Meta(EduModelSerializer.Meta):
        model = Education
        fields = '__all__'
        depth=1


class EducationViewSet(EduModelViewSet):

    class EducationPermissions(BasePermission):

        def has_permission(self, request: Request, view: "EducationViewSet"):
            if view.action == "create":
                return request_user_is_staff(request)
            else:
                return request_user_is_authenticated(request)

        def has_object_permission(self, request: Request, view: "EducationViewSet", obj: Education):
            if view.action in ["update", "partial_update", "destroy"]:
                return request_user_is_staff(request)
            else:
                return request_user_is_authenticated(request)

    serializer_class = EducationShallowSerializer
    authentication_classes = [MultiTokenAuthentication]
    permission_classes = [EducationPermissions]

    def get_queryset(self):
        u: User = self.request.user

        if isinstance(u, AnonymousUser):
            return None
        elif u.is_staff or u.is_superuser:
            return Education.objects.all()
        else:
            users = User.objects.filter(id=u.id) | u.children.all()
            return Education.objects.filter(student__in=users)


class EducationSpecializationViewSet(EduModelViewSet):

    class EducationSpecializationPermissions(BasePermission):

        def has_permission(self, request: Request, view: "CourseEnrollmentViewSet"):
            if view.action == "create":
                return request_user_is_staff(request)
            else:
                return request_user_is_authenticated(request)

        def has_object_permission(self, request: Request, view: "CourseEnrollmentViewSet", obj: EducationSpecialization):
            if view.action in ["update", "partial_update", "destroy"]:
                return request_user_is_staff(request)
            else:
                return request_user_is_authenticated(request)

    queryset = EducationSpecialization.objects.all()
    serializer_class = EducationSpecializationSerializer
    authentication_classes = [MultiTokenAuthentication]
    permission_classes = [EducationSpecializationPermissions]
