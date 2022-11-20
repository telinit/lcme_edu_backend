from django.contrib.auth.models import AnonymousUser
from django.db import transaction
from django.db.models import Q
from drf_yasg.utils import swagger_auto_schema
from rest_framework import serializers, viewsets, permissions
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import action
from rest_framework.fields import SerializerMethodField, UUIDField, DictField, ListField
from rest_framework.permissions import BasePermission
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import Serializer, ModelSerializer
from rest_framework.status import HTTP_403_FORBIDDEN, HTTP_404_NOT_FOUND, HTTP_400_BAD_REQUEST
from rest_framework_simplejwt.authentication import JWTAuthentication

from .models import Course, CourseEnrollment
from ..activity.api import ActivitySerializer
from ..activity.models import Activity
from ..common.api import ErrorMessageSerializer
from ..education.api import EducationSpecializationSerializer
from ..file.api import FileSerializer
from ..user.api import UserShallowSerializer
from ..user.auth import MultiTokenAuthentication
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


class BulkSetActivitiesSerializer(Serializer):

    # delete = ListField(child=UUIDField())
    create = ActivitySerializer(many=True)
    update = DictField(child=ActivitySerializer())


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
            elif view.action in ["bulk_set_activities"]:
                return request_user_is_authenticated(request) and \
                       (request_user_is_staff(request) or obj.teachers.filter(id=request.user.id).exists())
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

    @swagger_auto_schema(request_body=BulkSetActivitiesSerializer,
                         responses={200: 'OK', HTTP_400_BAD_REQUEST: ErrorMessageSerializer})
    @action(methods=['POST'], detail=True)
    def bulk_set_activities(self, request: Request, pk):
        course = Course.objects.filter(id=pk)
        if not course:
            return Response(status=HTTP_404_NOT_FOUND)

        course = course[0]
        ser = BulkSetActivitiesSerializer(data=request.data)

        if not ser.is_valid():
            return Response(
                status=HTTP_400_BAD_REQUEST,
                data={
                    'code': HTTP_400_BAD_REQUEST,
                    'message': str(ser.errors)
                }
            )

        dont_delete = []

        with transaction.atomic():
            for act_raw in ser.validated_data['create']:
                if act_raw['course'].id != course.id:
                    return Response(status=HTTP_400_BAD_REQUEST)

                act_raw_safe = dict(act_raw)
                if 'files' in act_raw_safe:
                    del act_raw_safe['files']

                act = Activity(**act_raw_safe)

                if 'files' in act_raw:
                    for f in act_raw['files']:
                        act.files.add(f)

                act.save()
                dont_delete += [act.id]

            for act_id, act_raw in ser.validated_data['update'].items():
                if act_raw['course'].id != course.id:
                    return Response(status=HTTP_400_BAD_REQUEST)

                act_raw_safe = dict(act_raw)
                if 'files' in act_raw_safe:
                    del act_raw_safe['files']

                act = Activity.objects.filter(id=act_id)\

                if 'files' in act_raw:
                    for f in act_raw['files']:
                        act.files.add(f)

                act.update(**act_raw_safe)
                dont_delete += [act_id]

            Activity.objects.filter(
                Q(course=course),
                ~Q(id__in=dont_delete),
            ).delete()

        return Response()

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
    authentication_classes = [MultiTokenAuthentication]
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

    authentication_classes = [MultiTokenAuthentication]
    permission_classes = [CourseEnrollmentPermissions]
    filterset_fields = ['person', 'course', 'role', 'finished_on']
