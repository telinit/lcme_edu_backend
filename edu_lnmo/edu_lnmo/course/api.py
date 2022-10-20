from django.contrib.auth.models import AnonymousUser
from rest_framework import serializers, viewsets, permissions
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.fields import SerializerMethodField
from rest_framework.permissions import BasePermission
from rest_framework.request import Request
from rest_framework_simplejwt.authentication import JWTAuthentication

from .models import Course, CourseEnrollment
from ..activity.api import ActivitySerializer
from ..education.api import EducationSpecializationSerializer
from ..file.api import FileSerializer
from ..user.api import UserSerializer
from ..user.models import User
from ..util.rest import EduModelViewSet, EduModelSerializer, request_user_is_staff, request_user_is_authenticated, \
    EduModelReadSerializer, EduModelWriteSerializer

class CourseEnrollmentReadSerializer(EduModelReadSerializer):
    person = UserSerializer()
    class Meta(EduModelSerializer.Meta):
        model = CourseEnrollment
        fields = '__all__'
        depth = 0


class CourseEnrollmentWriteSerializer(EduModelWriteSerializer):
    class Meta(EduModelSerializer.Meta):
        model = CourseEnrollment
        fields = '__all__'
        depth = 0


class CourseReadSerializer(EduModelReadSerializer):
    for_specialization = EducationSpecializationSerializer(allow_null=True)
    logo = FileSerializer(allow_null=True)
    cover = FileSerializer(allow_null=True)

    activities = ActivitySerializer(many=True) # SerializerMethodField()
    enrollments = CourseEnrollmentReadSerializer(many=True)


    class Meta(EduModelSerializer.Meta):
        model = Course
        fields = '__all__'
        depth = 1


class CourseWriteSerializer(EduModelWriteSerializer):
    class Meta(EduModelSerializer.Meta):
        model = Course
        fields = '__all__'
        depth = 0


class CourseSerializer(EduModelSerializer):
    # for_specialization = EducationSpecializationSerializer()
    # logo = FileSerializer()
    # cover = FileSerializer()

    class Meta(EduModelSerializer.Meta):
        model = Course
        fields = '__all__'


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
            ).all()
        else:
            users = User.objects.filter(id=u.id) | u.children.all()
            return CourseEnrollment.get_courses_of_user(users)

    def get_serializer_class(self):
        method = self.request.method
        if method == 'PUT' or method == 'POST':
            return CourseWriteSerializer
        else:
            return CourseReadSerializer

    serializer_class = CourseSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [CoursePermissions]
    filterset_fields = ['for_specialization', 'for_group', 'for_class']
    search_fields = ['title', 'description']


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
            return CourseEnrollment.objects.filter(person=u)

    def get_serializer_class(self):
        method = self.request.method
        if method == 'PUT' or method == 'POST':
            return CourseEnrollmentWriteSerializer
        else:
            return CourseEnrollmentReadSerializer

    authentication_classes = [TokenAuthentication]
    permission_classes = [CourseEnrollmentPermissions]
    filterset_fields = ['person', 'course', 'role', 'finished_on']
