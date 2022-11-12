import datetime
from csv import DictReader
from typing import Tuple, Any

from .user import generate_password
from ..common.models import Organization, Department
from ..course.models import Course, CourseEnrollment
from ..education.models import EducationSpecialization, Education
from ..imports.base import CSVDataImporter
from ..imports.user import create_user
from ..user.models import User


class PasswordsImportResult(object):
    objects = []
    report_rows = [["Фамилия","Имя","Отчество","Количество пользователей","Статус"]]

    def save_report(self, file_name: str):
        open(file_name, "w").writelines(map(lambda ws: ",".join(ws) + "\n", self.report_rows))


class PasswordsDataImporter(CSVDataImporter):

    @staticmethod
    def create_parent(child: User, first_name, middle_name, last_name):
        if first_name == "" and middle_name == "" and last_name == "":
            return None
        parent = create_user(first_name, middle_name, last_name)
        child.parents.add(parent)
        return parent

    def do_import(self, data: str, print_status_stdout_every=0):
        r = DictReader(data.splitlines())
        res = PasswordsImportResult()

        for i, rec in enumerate(r):
            last_name = rec["Фамилия"].strip()
            first_name = rec["Имя"].strip()
            middle_name = rec["Отчество"].strip()
            pwd = rec["Пароль"]

            user = User.objects.filter(
                last_name=last_name,
                first_name=first_name,
                middle_name=middle_name
            )

            if not user:
                res.report_rows += [[last_name, first_name, middle_name, "0", "Пропуск"]]
            else:
                count = user.count()
                if count > 1:
                    res.report_rows += [[last_name, first_name, middle_name, str(count), "Пропуск"]]
                else:
                    user = user[0]
                    user.set_password(pwd)
                    user.save()

                    res.report_rows += [[last_name, first_name, middle_name, str(count), "Успех"]]
                    res.objects += [user]

            if print_status_stdout_every > 0 and i % print_status_stdout_every == 0:
                print(f"PasswordsDataImporter: {i}")

        return res
