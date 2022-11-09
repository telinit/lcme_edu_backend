import uuid

from django.contrib.auth.models import AnonymousUser
from django.db.models import QuerySet
from rest_framework import viewsets, serializers, permissions
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.permissions import BasePermission
from rest_framework.request import Request

from .models import Activity
from ..course.models import Course, CourseEnrollment
from ..user.models import User
from ..util.rest import request_user_is_staff, EduModelViewSet, request_user_is_authenticated, EduModelSerializer, \
    EduModelReadSerializer


class ActivitySerializer(EduModelSerializer):
    class Meta(EduModelSerializer.Meta):
        model = Activity
        fields = '__all__'

    # TODO: Validate


class ActivityViewSet(EduModelViewSet):
    class ActivityPermissions(BasePermission):
        def has_write_access(self, request: Request):
            is_authenticated = request_user_is_authenticated(request)
            is_staff = lambda: request_user_is_staff(request)
            is_teacher = lambda: "course" in request.data and CourseEnrollment \
                .get_courses_of_teacher(request.user) \
                .filter(id=uuid.UUID(request.data["course"])) \
                .exists()

            return is_authenticated and (is_staff() or is_teacher())

        def has_permission(self, request: Request, view: "ActivityViewSet"):
            if view.action in ["create"]:
                return self.has_write_access(request)
            else:
                return request_user_is_authenticated(request)

        def has_object_permission(self, request: Request, view: "ActivityViewSet", obj: Activity):
            if view.action in ["update", "partial_update", "destroy"]:
                if "course" in request.data and uuid.UUID(request.data["course"]) != obj.course.id:
                    return False
                return self.has_write_access(request)
            else:
                return request_user_is_authenticated(request)

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
    authentication_classes = [TokenAuthentication]
    permission_classes = [ActivityPermissions]
    filterset_fields = ['type', 'course', 'group']
    search_fields = ['title', 'keywords']
