from .base import CSVDataImporter
from csv import DictReader

from .user import create_user
from ..common.models import Organization, Department
from ..course.models import Course, CourseEnrollment
from ..education.models import EducationSpecialization


class CoursesDataImporter(CSVDataImporter):
    def do_import(self, data: str):
        r = DictReader(data.splitlines())
        res = []
        for rec in r:
            last_name = rec["Фамилия преподавателя"].strip()
            first_name = rec["Имя преподавателя"].strip()
            middle_name = rec["Отчество преподавателя"].strip()

            if first_name == "" and middle_name == "" and last_name == "":
                continue

            org, _ = Organization.objects.get_or_create(
                name="Лаборатория Непрерывного Математического Образования",
                name_short="ЛНМО"
            )
            dep, _ = Department.objects.get_or_create(
                organization=org,
                name="Общая площадка"
            )
            spec, _ = EducationSpecialization.objects.get_or_create(
                name=rec["Направление"].strip(),
                department=dep
            )

            teacher = create_user(first_name, middle_name, last_name)

            course, _ = Course.objects.get_or_create(
                title=rec["Курс"].strip(),
                for_specialization=spec,
                for_class=rec["Класс"].strip(),
                for_group=rec["Группа"].strip(),
            )

            course_enrollment, _ = CourseEnrollment.objects.get_or_create(
                person=teacher,
                course=course,
                role=CourseEnrollment.EnrollmentRole.teacher,
                finished_on=None
            )

            res += [org, dep, spec, teacher, course, course_enrollment]

        return res
