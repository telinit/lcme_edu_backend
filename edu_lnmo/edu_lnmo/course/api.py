import datetime

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
from ..activity.models import Activity
from ..common.api import ErrorMessageSerializer
from ..user.api import UserShallowSerializer
from ..user.auth import MultiTokenAuthentication
from ..user.models import User
from ..util.email import EmailManager
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


class CourseSerializer(EduModelWriteSerializer):
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
            if view.action in ["update", "partial_update"]:
                teacher_updates_course = Course.objects.filter(
                    enrollments__person=request.user,
                    enrollments__role__in=[
                        CourseEnrollment.EnrollmentRole.manager,
                        CourseEnrollment.EnrollmentRole.teacher
                    ],
                    id=obj.id
                ).count() > 0

                return request_user_is_staff(request) or teacher_updates_course
            elif view.action == "destroy":
                return request_user_is_staff(request)
            elif view.action in ["bulk_set_activities"]:
                return request_user_is_authenticated(request) and \
                    (   request_user_is_staff(request)
                     or obj.teachers.filter(id=request.user.id).exists()
                     or obj.managers.filter(id=request.user.id).exists()
                )
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
            ).distinct().all()
        else:
            users = User.objects.filter(id=u.id) | u.children.all()
            return CourseEnrollment.get_courses_of_user(users).distinct()

    serializer_class = CourseSerializer
    authentication_classes = [MultiTokenAuthentication]
    permission_classes = [CoursePermissions]
    filterset_fields = {k: ['exact', 'isnull'] for k in ["for_specialization", "for_group", "for_class", "enrollments__person", "enrollments__role", "archived"]}
    search_fields = ["title", "description"]


class CourseEnrollmentViewSet(EduModelViewSet):
    class CourseEnrollmentPermissions(BasePermission):

        def has_permission(self, request: Request, view: "CourseEnrollmentViewSet"):
            if view.action == "create":
                def teacher_adds_student_or_listener():
                    if not request_user_is_authenticated(request) or not request.data:
                        return False

                    p = CourseEnrollmentWriteSerializer(data=request.data)

                    if not p.is_valid():
                        return False

                    in_role_ok = p.validated_data['role'] in [
                            CourseEnrollment.EnrollmentRole.student,
                            CourseEnrollment.EnrollmentRole.listener
                        ]

                    teacher_is_enrolled = lambda:CourseEnrollment \
                            .get_courses_of_teacher(request.user) \
                            .filter(id=p.validated_data['course'].id) \
                            .exists()

                    return in_role_ok and teacher_is_enrolled()

                return request_user_is_staff(request) or teacher_adds_student_or_listener()
            else:
                return request_user_is_authenticated(request)

        def has_object_permission(self, request: Request, view: "CourseEnrollmentViewSet", obj: CourseEnrollment):
            if view.action in ["destroy"]:
                return request_user_is_staff(request)
            elif view.action in ["update", "partial_update"]:
                def teacher_updates_student_or_listener() -> bool:
                    if not request_user_is_authenticated(request):
                        return False

                    p = CourseEnrollmentWriteSerializer(data=request.data)

                    if not p.is_valid():
                        return False

                    payload_role_ok = p.validated_data['role'] in [
                            CourseEnrollment.EnrollmentRole.student,
                            CourseEnrollment.EnrollmentRole.listener
                        ]

                    obj_role_ok = obj.role in [
                            CourseEnrollment.EnrollmentRole.student,
                            CourseEnrollment.EnrollmentRole.listener
                        ]

                    same_person = p.validated_data["person"] == obj.person

                    same_course = p.validated_data["course"] == obj.course

                    not_finished = obj.finished_on is None

                    teacher_enrolled = obj.course and CourseEnrollment \
                        .get_courses_of_teacher(request.user) \
                        .filter(id=obj.course.id) \
                        .exists()

                    return payload_role_ok and same_person and same_course and not_finished and \
                            obj_role_ok and teacher_enrolled

                def manager_does_stuff() -> bool:
                    p = CourseEnrollmentWriteSerializer(data=request.data)

                    if not p.is_valid():
                        return False

                    is_manager = CourseEnrollment.objects.filter(
                        course=obj.course,
                        person=request.user,
                        role=CourseEnrollment.EnrollmentRole.manager
                    ).exists()

                    payload_role_ok = p.validated_data['role'] != CourseEnrollment.EnrollmentRole.manager
                    modify_self = p.validated_data['person'] == request.user
                    not_finished = obj.finished_on is None

                    return is_manager and (payload_role_ok or modify_self) and not_finished

                return request_user_is_staff(request) or teacher_updates_student_or_listener() or manager_does_stuff()
            else:
                return request_user_is_authenticated(request)

    def get_queryset(self):
        u: User = self.request.user

        if isinstance(u, AnonymousUser):
            return None
        else:
            return CourseEnrollment.objects.all()

    def get_serializer_class(self):
        method = self.request.method
        if method == 'PUT' or method == 'POST':
            return CourseEnrollmentWriteSerializer
        else:
            return CourseEnrollmentReadSerializer

    authentication_classes = [MultiTokenAuthentication]
    permission_classes = [CourseEnrollmentPermissions]
    filterset_fields = dict((k, ['exact', 'isnull']) for k in ['person', 'course', 'role', 'finished_on'])
