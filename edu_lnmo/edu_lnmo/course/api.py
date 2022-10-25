from django.contrib.auth.models import AnonymousUser
from drf_yasg.utils import swagger_auto_schema
from rest_framework import serializers, viewsets, permissions
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.decorators import action
from rest_framework.fields import SerializerMethodField
from rest_framework.permissions import BasePermission
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.status import HTTP_403_FORBIDDEN, HTTP_404_NOT_FOUND
from rest_framework_simplejwt.authentication import JWTAuthentication

from .models import Course, CourseEnrollment
from ..activity.api import ActivitySerializer
from ..education.api import EducationSpecializationSerializer
from ..file.api import FileSerializer
from ..user.api import UserShallowSerializer
from ..user.models import User
from ..util.rest import EduModelViewSet, EduModelSerializer, request_user_is_staff, request_user_is_authenticated, \
    EduModelReadSerializer, EduModelWriteSerializer

class CourseEnrollmentReadSerializer(EduModelReadSerializer):
    person = UserShallowSerializer()
    class Meta(EduModelSerializer.Meta):
        model = CourseEnrollment
        fields = '__all__'
        depth = 0


class CourseEnrollmentWriteSerializer(EduModelWriteSerializer):
    class Meta(EduModelSerializer.Meta):
        model = CourseEnrollment
        fields = '__all__'
        depth = 0


class CourseDeepSerializer(EduModelReadSerializer):
    for_specialization = EducationSpecializationSerializer(allow_null=True)
    logo = FileSerializer(allow_null=True)
    cover = FileSerializer(allow_null=True)

    activities = ActivitySerializer(many=True) # SerializerMethodField()
    enrollments = CourseEnrollmentReadSerializer(many=True)


    class Meta(EduModelSerializer.Meta):
        model = Course
        fields = '__all__'
        depth = 1


class CourseShallowSerializer(EduModelWriteSerializer):
    class Meta(EduModelSerializer.Meta):
        model = Course
        fields = '__all__'
        depth = 0


class CourseViewSet(EduModelViewSet):
    class CoursePermissions(BasePermission):

        def has_permission(self, request: Request, view: "CourseViewSet"):
            if view.action == "create":
                return request_user_is_staff(request)
            else:
                return request_user_is_authenticated(request)

        def has_object_permission(self, request: Request, view: "CourseViewSet", obj: Course):
            if view.action in ["update", "partial_update", "destroy"]:
                return request_user_is_staff(request)
            else:
                return request_user_is_authenticated(request)

    @swagger_auto_schema(responses={200: CourseDeepSerializer()})
    @action(methods=['GET'], detail=True, url_path='deep')
    def get_deep(self, request: Request, pk, *args, **kwargs):
        obj = self.get_queryset().filter(id=pk)
        if not obj:
            return Response(status=HTTP_404_NOT_FOUND)
        else:
            obj = obj.get()
            ser = CourseDeepSerializer(obj)
            return Response(ser.data)

    @swagger_auto_schema(responses={200: CourseDeepSerializer()})
    @action(methods=['GET'], detail=False, url_path='deep')
    def list_deep(self, request: Request, *args, **kwargs):
        obj = self.get_queryset()
        ser = CourseDeepSerializer(obj, many=True)
        return Response(ser.data)

    def get_queryset(self):
        u: User = self.request.user

        if isinstance(u, AnonymousUser):
            return None
        elif u.is_staff or u.is_superuser:
            return Course.objects.prefetch_related(
                "for_specialization",
                "logo",
                "cover",
                "activities",
                "enrollments"
            ).distinct().all()
        else:
            users = User.objects.filter(id=u.id) | u.children.all()
            return CourseEnrollment.get_courses_of_user(users).distinct()

    serializer_class = CourseShallowSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [CoursePermissions]
    filterset_fields = ["for_specialization", "for_group", "for_class", "enrollments__person", "enrollments__role"]
    search_fields = ["title", "description"]


class CourseEnrollmentViewSet(EduModelViewSet):
    class CourseEnrollmentPermissions(BasePermission):

        def has_permission(self, request: Request, view: "CourseEnrollmentViewSet"):
            if view.action == "create":
                return request_user_is_staff(request)
            else:
                return request_user_is_authenticated(request)

        def has_object_permission(self, request: Request, view: "CourseEnrollmentViewSet", obj: CourseEnrollment):
            if view.action in ["update", "partial_update", "destroy"]:
                return request_user_is_staff(request)
            else:
                return request_user_is_authenticated(request)

    def get_queryset(self):
        u: User = self.request.user

        if isinstance(u, AnonymousUser):
            return None
        elif u.is_staff or u.is_superuser:
            return CourseEnrollment.objects.all()
        else:
            return CourseEnrollment.objects.filter(Q(person=u) | Q(person__in=u.children))

    def get_serializer_class(self):
        method = self.request.method
        if method == 'PUT' or method == 'POST':
            return CourseEnrollmentWriteSerializer
        else:
            return CourseEnrollmentReadSerializer

    authentication_classes = [TokenAuthentication]
    permission_classes = [CourseEnrollmentPermissions]
    filterset_fields = ['person', 'course', 'role', 'finished_on']
