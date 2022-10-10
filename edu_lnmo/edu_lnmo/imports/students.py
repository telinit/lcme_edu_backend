from csv import DictReader

from ..common.models import Organization, Department
from ..course.models import Course, CourseEnrollment
from ..education.models import EducationSpecialization
from ..imports.base import CSVDataImporter
from ..imports.user import create_user
from ..user.models import User


class StudentsDataImporter(CSVDataImporter):

    @staticmethod
    def create_parent(child: User, first_name, middle_name, last_name):
        if first_name == "" and middle_name == "" and last_name == "":
            return None
        parent = create_user(first_name, middle_name, last_name)
        child.parents.add(parent)
        return parent

    def do_import(self, data: str):
        r = DictReader(data.splitlines())
        res = []
        for rec in r:
            last_name = rec["Фамилия учащегося"].strip()
            first_name = rec["Имя учащегося"].strip()
            middle_name = rec["Отчество учащегося"].strip()

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

            student = create_user(first_name, middle_name, last_name)

            parent1 = self.create_parent(
                student,
                rec["Имя родителя 1"].strip(),
                rec["Отчество родителя 1"].strip(),
                rec["Фамилия родителя 1"].strip()
            )

            parent2 = self.create_parent(
                student,
                rec["Имя родителя 2"].strip(),
                rec["Отчество родителя 2"].strip(),
                rec["Фамилия родителя 2"].strip()
            )

            courses = Course.objects.filter(
                for_class=rec["Класс"].strip(),
                for_group=""
            )

            course_enrollments = []

            for course in courses:
                course_enrollment, _ = CourseEnrollment.objects.get_or_create(
                    person=student,
                    course=course,
                    role=CourseEnrollment.EnrollmentRole.student,
                    finished_on=None
                )

            res += [org, dep, spec, student, parent1, parent2] + course_enrollments

        return res
