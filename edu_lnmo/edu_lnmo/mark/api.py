from uuid import UUID

from django.contrib.auth.models import AnonymousUser
from django.db.models import Q, QuerySet
from rest_framework import permissions, viewsets, serializers
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.permissions import BasePermission
from rest_framework.request import Request
from rest_framework_simplejwt.authentication import JWTAuthentication

from .models import Mark
from ..activity.models import Activity
from ..course.models import CourseEnrollment, Course
from ..user.models import User
from ..util.rest import EduModelViewSet, EduModelSerializer, request_user_is_staff, request_user_is_authenticated


class MarkSerializer(EduModelSerializer):
    class Meta(EduModelSerializer.Meta):
        model = Mark
        fields = '__all__'

    def validate(self, data):
        cond1 = "activity" in data and data["activity"]
        cond2 = "course" in data and data["course"]

        # TODO: Check if fields are set according to the type

        return (cond1 != cond2) and super().validate(data)


class MarkViewSet(EduModelViewSet):
    class MarkPermissions(BasePermission):

        def has_permission(self, request: Request, view: "MarkViewSet"):
            if view.action == "create":  # TODO: Refactor this
                if not request_user_is_authenticated(request):
                    return False
                elif "activity" in request.data:
                    activity: QuerySet = Activity.objects\
                        .select_related("marks", "course")\
                        .filter(id=UUID(request.data["activity"]))
                    student = User(id=UUID(request.data["student"]))

                    if not activity:
                        return False

                    activity: Activity = activity[0]

                    if Mark.objects.filter(activity=activity).count() >= activity.marks_limit:
                        return False

                    course = Course.objects.filter(id=activity.course.id)
                    teachers = CourseEnrollment\
                        .get_teachers_of_courses(course)\
                        .filter(person=request.user)
                    students = CourseEnrollment\
                        .get_students_of_courses(course)\
                        .filter(person=student)

                    if teachers.exists() and students.exists():
                        return True

                    return False
                elif "course" in request.data:
                    student = User(id=UUID(request.data["student"]))
                    course = Course.objects.filter(id=UUID(request.data["course"]))
                    teachers = CourseEnrollment \
                        .get_teachers_of_courses(course) \
                        .filter(person=request.user)
                    students = CourseEnrollment \
                        .get_students_of_courses(course) \
                        .filter(person=student)

                    if teachers.exists() and students.exists():
                        return True
                else:
                    return False

                return request_user_is_staff(request)
            else:
                return request_user_is_authenticated(request)

        def has_object_permission(self, request: Request, view: "MarkViewSet", obj: Mark):
            if view.action in ["update", "partial_update", "destroy"]:
                return request_user_is_staff(request) or \
                       CourseEnrollment.get_teachers_of_courses( obj.get_course() ).filter(id=request.user.id).exists()
            else:
                return request_user_is_authenticated(request)

    def get_queryset(self):
        u: User = self.request.user

        if isinstance(u, AnonymousUser):
            return None
        elif u.is_staff or u.is_superuser:
            return Mark.objects.all()
        else:
            users = User.objects.filter(id=u.id) | u.children.all()

            q1 = Q(teacher__in=users)
            q2 = Q(student__in=users)

            courses = CourseEnrollment.get_courses_of_user(users)

            q3 = Q(course__in=courses)
            q4 = Q(activity__course__in=courses)

            return Mark.objects.filter(q1 | q2 | q3 | q4)

    serializer_class = MarkSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [MarkPermissions]
