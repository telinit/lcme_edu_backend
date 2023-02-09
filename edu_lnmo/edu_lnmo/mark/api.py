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
                is_getting_self = lambda : \
                    request and request.GET and \
                    request.user and request.user.id and \
                    str(request.GET.get("student")) == str(request.user.id)
                is_getting_child = lambda: \
                    request and request.GET and \
                    request.user and request.user.id and \
                    request.user.children.filter(id=str(request.GET.get("student"))).exists()
                return request_user_is_staff(request) or is_getting_self() or is_getting_child()
            elif view.action == "create":  # TODO: Refactor this
                if not request_user_is_authenticated(request):
                    return False
                elif request_user_is_staff(request):
                    return True
                elif "activity" in request.data:
                    activity: QuerySet = Activity.objects\
                        .select_related("course")\
                        .filter(id=UUID(request.data["activity"]))
                    student = User(id=UUID(request.data["student"]))

                    if not activity:
                        return False

                    activity: Activity = activity[0]

                    if Mark.objects.filter(activity=activity, student=student).count() >= activity.marks_limit:
                        return False

                    course = Course.objects.filter(id=activity.course.id)
                    teachers = CourseEnrollment\
                        .get_teachers_of_courses(course, id=request.user.id)
                    students = CourseEnrollment\
                        .get_students_of_courses(course, id=student.id)

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

                return False
            else:
                return request_user_is_authenticated(request)

        def has_object_permission(self, request: Request, view: "MarkViewSet", obj: Mark):
            if view.action in ["update", "partial_update", "destroy"]:
                return request_user_is_staff(request) or \
                       CourseEnrollment.get_teachers_of_courses( [obj.activity.course ]).filter(id=request.user.id).exists()
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

            courses = CourseEnrollment.get_courses_of_teacher(u)
            q3 = Q(activity__course__in=courses)

            return Mark.objects.filter(q1 | q2 | q3)

    serializer_class = MarkSerializer
    authentication_classes = [MultiTokenAuthentication, SessionAuthentication]
    permission_classes = [MarkPermissions]

    filterset_fields = ["author", "student", "value", "activity", "activity__course"]
    search_fields = ["comment"]

    def export_csv_make_row(self, student, education, enrollment, csv_out):
        course = enrollment.course

        marks = [
            *Mark.objects
                .filter(activity__course=course, student=student)
                .order_by('activity__order')
                .prefetch_related('activity')
        ]

        fins: dict[str, tuple[int, int]] = {}
        for i, m in enumerate(marks):
            if m.activity.content_type == Activity.ActivityContentType.FIN:
                ft = m.activity.final_type
                if ft in fins:
                    fins[ft] = (fins[ft][0], i)
                else:
                    fins[ft] = (i, i)

        mark_values = lambda ms: " ".join(map(lambda m: m.value, ms))

        def segment_marks(start_fin_types: Iterable, end_fin_types: Iterable, include_start=False,
                          include_end=False) -> str:
            get_fin = lambda ft: [*fins[ft]] if ft in fins else []

            fin_start_ranges: list[list[int]] = [*map(get_fin, start_fin_types)]
            ss: list[int] = sum(fin_start_ranges, []) if len(fin_start_ranges) > 0 else []
            if len(ss) > 0:
                start = max(ss) + 1 if not include_start else min(ss)
            else:
                start = 0

            fin_end_ranges: list[list[int]] = [*map(get_fin, end_fin_types)]
            es: list[int] = sum(fin_end_ranges, []) if len(fin_end_ranges) > 0 else []
            if len(es) > 0:
                end = min(es) if not include_end else max(es) + 1
            else:
                end = 0

            if start > end:
                return "Некорректно заданы границы периода в курсе"
            else:
                return mark_values(marks[start:end])

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

    def export_csv(self, request: Request, archive_group_by_person = False):
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
            educations = Education.objects.filter(student=student).order_by('-started')[:1].prefetch_related('specialization')
            education = educations[0] if educations else None
            enrollments = CourseEnrollment.objects.filter(person=student, role=CourseEnrollment.EnrollmentRole.student).prefetch_related('course')

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