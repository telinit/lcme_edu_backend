import uuid

from django.contrib.auth.models import AnonymousUser
from django.db import transaction
from django.db.models import QuerySet
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets, serializers, permissions
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import action
from rest_framework.fields import CharField, IntegerField, UUIDField
from rest_framework.permissions import BasePermission
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import Serializer
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_200_OK

from .models import Activity
from ..common.api import ErrorMessageSerializer
from ..course.models import Course, CourseEnrollment
from ..imports.activities import ActivitiesDataImporter
from ..user.auth import MultiTokenAuthentication
from ..user.models import User
from ..util.rest import request_user_is_staff, EduModelViewSet, request_user_is_authenticated, EduModelSerializer, \
    EduModelReadSerializer


class ActivitySerializer(EduModelSerializer):
    class Meta(EduModelSerializer.Meta):
        model = Activity
        fields = '__all__'


class ImportForCourseSerializer(Serializer):
    data        = CharField()
    sep         = CharField()
    course_id   = UUIDField()


class ImportForCourseResultSerializer(Serializer):
    class ImportForCourseResultObject(Serializer):
        index = IntegerField()
        type = CharField()
        topic = CharField()

    objects = ImportForCourseResultObject(many=True)


class ActivityViewSet(EduModelViewSet):
    class ActivityPermissions(BasePermission):
        def has_write_access(self, request: Request, obj: Activity):
            is_authenticated = request_user_is_authenticated(request)
            is_staff = lambda: request_user_is_staff(request)
            is_teacher = lambda: CourseEnrollment \
                .get_courses_of_teacher(request.user) \
                .filter(id=obj.course.id) \
                .exists()

            is_manager = lambda: CourseEnrollment.objects.filter(
                    person=request.user,
                    course=obj.course,
                    role=CourseEnrollment.EnrollmentRole.manager,
                    finished_on__isnull=True
                ).exists()

            return is_authenticated and (is_staff() or is_teacher() or is_manager())

        def has_permission(self, request: Request, view: "ActivityViewSet"):
            if view.action in ["create"]:
                return self.has_write_access(request)
            else:
                return request_user_is_authenticated(request)

        def has_object_permission(self, request: Request, view: "ActivityViewSet", obj: Activity):
            if view.action == "destroy":
                return self.has_write_access(request, obj)
            elif view.action in ["update", "partial_update"]:
                same_course = ("course" in request.data) and uuid.UUID(request.data["course"]) == obj.course.id

                return same_course and self.has_write_access(request, obj)
            else:
                return request_user_is_authenticated(request)

    @swagger_auto_schema(request_body=ImportForCourseSerializer,
                         responses={
                             HTTP_200_OK: ImportForCourseResultSerializer(),
                             HTTP_400_BAD_REQUEST: ErrorMessageSerializer()
                         })
    @action(methods=['POST'], detail=False)
    def import_for_course(self, request: Request):
        ser = ImportForCourseSerializer(data=request.data)

        if not ser.is_valid():
            return Response(
                status=HTTP_400_BAD_REQUEST,
                data={
                    'code': HTTP_400_BAD_REQUEST,
                    'message': str(ser.errors)
                }
            )

        with transaction.atomic():
            data = ser.validated_data['data']
            course_id = ser.validated_data['course_id']
            sep = ser.validated_data['sep']

            imp = ActivitiesDataImporter()
            import_result = imp.do_import(data, course_id, sep=sep)

            result_data = []
            for r in import_result.report_rows[1:]:
                result_data += [{"index": int(r[0]), "type": r[1], "topic": r[2]}]

            return Response(data={"objects": result_data})

    def get_queryset(self):
        u: User = self.request.user

        if isinstance(u, AnonymousUser):
            return None
        elif u.is_staff or u.is_superuser:
            return Activity.objects.all()
        else:
            users: QuerySet = User.objects.filter(id=u.id) | u.children.all()
            courses: QuerySet = CourseEnrollment.get_courses_of_user(users)
            if not courses:
                return []
            else:
                activities = courses[0].activities.all()
                for c in courses[1:]:
                    activities |= c.activities.all()
                return activities

    serializer_class = ActivitySerializer
    authentication_classes = [MultiTokenAuthentication]
    permission_classes = [ActivityPermissions]
    filterset_fields = ['content_type', 'course', 'group', 'course__enrollments__person', 'course__archived']
    search_fields = ['title', 'keywords', 'lesson_type']
