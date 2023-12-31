import datetime
from csv import DictReader
from datetime import datetime
from typing import Tuple, Any, Optional

from django.db.models import Q

from .user import generate_password
from ..common.models import Organization, Department
from ..course.models import Course, CourseEnrollment
from ..education.models import EducationSpecialization, Education
from ..imports.base import CSVDataImporter
from ..imports.user import create_user
from ..user.models import User


class StudentsImportResult(object):
    objects = []
    report_rows = [["Фамилия","Имя","Отчество","Направление обучения","Класс","Родитель?","Логин","Пароль"]]

    def __init__(self):
        self.objects = []
        self.report_rows = [["Фамилия","Имя","Отчество","Направление обучения","Класс","Родитель?","Логин","Пароль"]]

    def save_report(self, file_name: str):
        open(file_name, "w").writelines(map(lambda ws: ",".join(ws) + "\n", self.report_rows))


class StudentsDataImporter(CSVDataImporter):

    @staticmethod
    def create_parent(child: User, first_name: str, middle_name: str, last_name: str) -> Tuple[Optional[User], bool]:
        if first_name == "" and middle_name == "" and last_name == "":
            return None, False
        parent, created = create_user(first_name, middle_name, last_name)
        child.parents.add(parent)
        return parent, created

    def do_import(self, data: str, **kwargs):
        r = DictReader(data.splitlines())
        res = StudentsImportResult()
        users = {}
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
            spec, _= EducationSpecialization.objects.get_or_create(
                name=rec["Направление"].strip(),
                department=dep
            )

            student = create_user(first_name, middle_name, last_name)

            parent1 = self.create_parent(
                student[0],
                rec["Имя родителя 1"].strip(),
                rec["Отчество родителя 1"].strip(),
                rec["Фамилия родителя 1"].strip()
            )

            parent2 = self.create_parent(
                student[0],
                rec["Имя родителя 2"].strip(),
                rec["Отчество родителя 2"].strip(),
                rec["Фамилия родителя 2"].strip()
            )

            existing_edu = Education.objects.filter(
                student=student[0],
                finished=None
            ).order_by("-started")

            if existing_edu and existing_edu[0].specialization == spec:
                edu = existing_edu[0]
            else:
                existing_edu.update(finished=datetime.date.today())
                edu, _ = Education.objects.get_or_create(
                    student=student[0],
                    started=datetime.date((datetime.date.today() - datetime.timedelta(days=31*6)).year, 9, 1),
                    starting_class=rec["Класс"].strip(),
                    specialization=spec
                )

            courses = Course.objects.filter(
                for_class=rec["Класс"].strip(),
                for_group="",
                for_specialization=spec,
                archived=None
            )

            course_enrollments = []

            for course in courses:
                course_enrollment, _ = CourseEnrollment.objects.get_or_create(
                    person=student[0],
                    course=course,
                    role=CourseEnrollment.EnrollmentRole.student,
                    finished_on=None
                )

            res.objects += [org, dep, spec, student, parent1, parent2] + course_enrollments

            objs: list[ Tuple[Tuple[User,bool], bool, EducationSpecialization, Education] ] \
                = [(student, False, spec, edu), (parent1, True, spec, edu), (parent2, True, spec, edu)]
            for t in objs:
                u: User = t[0][0]
                if u is None:
                    continue
                k = u.full_name()
                if k not in users:
                    users[k] = t

        for (user, created), is_parent, spec, edu in users.values():
            if created:
                pw = generate_password()
                user.set_password(pw)
                user.save()
            else:
                pw = "DID NOT CHANGE"

            res.report_rows += [[
                user.last_name,
                user.first_name,
                user.middle_name,
                spec.name,
                edu.starting_class,
                "Да" if is_parent else "Нет",
                user.username,
                pw
            ]]

        return res
