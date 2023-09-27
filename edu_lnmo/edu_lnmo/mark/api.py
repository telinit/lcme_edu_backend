import csv
import datetime
import itertools
import zipfile
from io import StringIO
from tempfile import SpooledTemporaryFile
from typing import Iterable
from uuid import UUID

from django.contrib.auth.models import AnonymousUser
from django.db.models import Q, QuerySet
from django.http import StreamingHttpResponse, HttpResponse
from drf_yasg.utils import swagger_auto_schema
from rest_framework import permissions, viewsets, serializers
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import action
from rest_framework.permissions import BasePermission
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK
from rest_framework_simplejwt.authentication import JWTAuthentication

from .models import Mark
from ..activity.models import Activity
from ..course.models import CourseEnrollment, Course
from ..education.models import Education
from ..user.auth import MultiTokenAuthentication
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
            if view.action == "export":
                is_getting_self = lambda: \
                    request and request.GET and \
                    request.user and request.user.id and \
                    str(request.GET.get("student")) == str(request.user.id)
                is_getting_child = lambda: \
                    request and request.GET and \
                    request.user and request.user.id and \
                    request.user.children.filter(id=str(request.GET.get("student"))).exists()
                return request_user_is_staff(request) or is_getting_self() or is_getting_child()
            elif view.action == "create":
                if not request_user_is_authenticated(request):
                    return False
                elif request_user_is_staff(request):
                    return True
                else:
                    p = MarkSerializer(data=request.data)
                    if not p.is_valid():
                        return False

                    student = p.validated_data["student"]
                    if not student:
                        return False

                    activity = p.validated_data["activity"]
                    if not activity:
                        return False

                    course = activity.course

                    enrolled_and_has_access = CourseEnrollment.objects\
                        .filter(
                            course=course,
                            person=request.user,
                            role__in=[CourseEnrollment.EnrollmentRole.teacher, CourseEnrollment.EnrollmentRole.manager]
                        ).exists()

                    student_enrolled = CourseEnrollment.objects\
                        .filter(
                            course=course,
                            person=student,
                            role=CourseEnrollment.EnrollmentRole.student
                        ).exists()

                    mark_limit_ok = Mark.objects.filter(activity=activity, student=student).count() <= activity.marks_limit

                    author_ok = p.validated_data["author"] == request.user

                    return enrolled_and_has_access and student_enrolled and mark_limit_ok and author_ok
            else:
                return request_user_is_authenticated(request)

        def has_object_permission(self, request: Request, view: "MarkViewSet", obj: Mark):
            if view.action in ["update", "partial_update", "destroy"]:
                enrolled_and_has_access = CourseEnrollment.objects \
                    .filter(
                    course=obj.activity.course,
                    person=request.user,
                    role__in=[CourseEnrollment.EnrollmentRole.teacher, CourseEnrollment.EnrollmentRole.manager]
                ).exists()
                return request_user_is_staff(request) or enrolled_and_has_access
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

            q1 = Q(author=u)
            q2 = Q(student__in=users)

            courses = Course.objects.filter(
                enrollments__person=u,
                enrollments__role__in=[CourseEnrollment.EnrollmentRole.teacher, CourseEnrollment.EnrollmentRole.manager, CourseEnrollment.EnrollmentRole.observer],
                enrollments__finished_on__isnull=True
            )
            q3 = Q(activity__course__in=courses)

            return Mark.objects.filter(q1 | q2 | q3)

    serializer_class = MarkSerializer
    authentication_classes = [MultiTokenAuthentication, SessionAuthentication]
    permission_classes = [MarkPermissions]

    filterset_fields = ["author", "student", "value", "activity", "activity__course", "activity__course__archived"]
    search_fields = ["comment"]

    def export_csv_make_row(self, student, education, enrollment, csv_out):
        course = enrollment.course

        marks = Mark.objects\
            .filter(activity__course=course, student=student)\
            .order_by('activity__order')

        acts: list[Activity] = [*Activity.objects
        .filter(course=course)
        .order_by('order')]

        act_marks_ix: dict[Activity, list[Mark]] = {}
        for m in marks:
            if m.activity in act_marks_ix:
                act_marks_ix[m.activity].append(m)
            else:
                act_marks_ix[m.activity] = [m]

        mark_values = lambda ms: " ".join(map(lambda m: m.value, ms))

        def find_latest_activity_by_types(types: Iterable[Activity.FinalType]) -> int:
            res = -1

            for i, act in enumerate(acts):
                if act.final_type in types:
                    res = i

            return res

        def collect_marks(activities: Iterable[Activity]) -> list[Mark]:
            res = []
            for act in activities:
                if act in act_marks_ix:
                    res += act_marks_ix[act]

            return res

        def segment_marks(start_fin_types: list[Activity.FinalType], end_fin_types: list[Activity.FinalType], include_start=False,
                          include_end=False) -> str:
            if start_fin_types == []:
                start = 0
            else:
                start = find_latest_activity_by_types(start_fin_types) + (0 if include_start else 1)

            if end_fin_types == []:
                end = len(acts) - 1
            else:
                end = find_latest_activity_by_types(end_fin_types) - (0 if include_end else 1)

            if start < 0 or end < 0 or start > end:
                return "Не найдено"
            else:
                return mark_values(collect_marks(acts[start:end+1]))

        data = {}

        data["Фамилия"] = str(student.last_name).strip()
        data["Имя"] = str(student.first_name).strip()
        data["Отчество"] = str(student.middle_name).strip()
        data["Класс"] = education.get_current_class() if education else "Н/Д"
        data["Направление обучения"] = education.specialization.name if education else "Н/Д"
        data["Предмет"] = course.title

        data["Текущие оценки (1)"] = segment_marks([], [Activity.FinalType.Q1])
        data["1 четверть"] = segment_marks([Activity.FinalType.Q1], [Activity.FinalType.Q1],
                                           include_start=True, include_end=True)
        data["Текущие оценки (2)"] = segment_marks([Activity.FinalType.Q1], [Activity.FinalType.Q2])
        data["2 четверть"] = segment_marks([Activity.FinalType.Q2], [Activity.FinalType.Q2],
                                           include_start=True, include_end=True)
        data["1 полугодие"] = segment_marks([Activity.FinalType.H1], [Activity.FinalType.H1],
                                            include_start=True, include_end=True)
        data["Текущие оценки (3)"] = segment_marks([Activity.FinalType.Q2, Activity.FinalType.H1],
                                                   [Activity.FinalType.Q3])
        data["3 четверть"] = segment_marks([Activity.FinalType.Q3], [Activity.FinalType.Q3],
                                           include_start=True, include_end=True)
        data["Текущие оценки (4)"] = segment_marks([Activity.FinalType.Q3],
                                                   [Activity.FinalType.Q4, Activity.FinalType.H2,
                                                    Activity.FinalType.Y])
        data["4 четверть"] = segment_marks([Activity.FinalType.Q4], [Activity.FinalType.Q4],
                                           include_start=True, include_end=True)
        data["2 полугодие"] = segment_marks([Activity.FinalType.H2], [Activity.FinalType.H2],
                                            include_start=True, include_end=True)
        data["Итог"] = segment_marks([Activity.FinalType.Y], [Activity.FinalType.Y],
                                     include_start=True, include_end=True)

        csv_out.writerow(data)

    def export_csv(self, request: Request, archive_group_by_person=False):
        try:
            students = User.objects.get(id=request.GET.get("student"))
        except:
            students = User.objects.filter(enrollments__role=CourseEnrollment.EnrollmentRole.student).distinct()

        def init_csv():
            out_buff = StringIO()
            csv_out = csv.DictWriter(out_buff, fieldnames=["Фамилия",
                                                           "Имя",
                                                           "Отчество",
                                                           "Класс",
                                                           "Направление обучения",
                                                           "Предмет",
                                                           "Текущие оценки (1)",
                                                           "1 четверть",
                                                           "Текущие оценки (2)",
                                                           "2 четверть",
                                                           "1 полугодие",
                                                           "Текущие оценки (3)",
                                                           "3 четверть",
                                                           "Текущие оценки (4)",
                                                           "4 четверть",
                                                           "2 полугодие",
                                                           "Итог"])

            csv_out.writeheader()

            return out_buff, csv_out

        out_buff, csv_out = init_csv()

        if archive_group_by_person:
            file = SpooledTemporaryFile()
            zip = zipfile.ZipFile(file, mode="x")

        for student in students:
            educations = Education.objects.filter(student=student).order_by('-started')[:1].prefetch_related(
                'specialization')
            education = educations[0] if educations else None
            enrollments = CourseEnrollment.objects.filter(person=student,
                                                          role=CourseEnrollment.EnrollmentRole.student).prefetch_related(
                'course')

            for enrollment in enrollments:
                self.export_csv_make_row(student, education, enrollment, csv_out)

            if archive_group_by_person:
                out_buff.seek(0)

                s = education.specialization.name if education else "Без направления"
                c = education.get_current_class() if education else "Без класса"
                l = student.last_name
                f = student.first_name
                m = student.middle_name
                fn = f"{s}/{c}/{l}_{f}_{m}.csv"

                zip.writestr(fn, out_buff.read())
                out_buff, csv_out = init_csv()

        if archive_group_by_person:
            zip.close()
            file.seek(0)

            response = HttpResponse(file, status=HTTP_200_OK, content_type="application/zip", )
            response['Content-Disposition'] = f'attachment; filename="marks_export_{datetime.datetime.now()}.zip"'
        else:
            out_buff.seek(0)
            response = HttpResponse(out_buff.read(), status=HTTP_200_OK, content_type="text/csv", )
            response['Content-Disposition'] = f'attachment; filename="marks_export_{datetime.datetime.now()}.csv"'

        return response

    @swagger_auto_schema()
    @action(methods=["GET"], detail=False, url_path="export", name="export")
    def export(self, request: Request):
        try:
            type_ = request.GET.get("type")
            if not type_ or str(type_).strip() == "":
                type_ = "csv_full"
        except:
            type_ = "csv_full"

        if type_ == "csv_full":
            return self.export_csv(request)
        elif type_ == "csv_archive":
            return self.export_csv(request, True)
