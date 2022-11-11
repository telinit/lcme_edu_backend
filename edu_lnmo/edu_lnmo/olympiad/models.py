import uuid

from django.db.models import *

from ..common.models import CommonObject, Department
from ..course.models import Course
from ..file.models import File
from ..user.models import User


class Olympiad(CommonObject):
    name = CharField(verbose_name="Название", max_length=255, null=False, blank=False)
    category = CharField(verbose_name="Предметная область", max_length=255, null=False, blank=False)
    website = URLField(verbose_name="Сайт олимпиады", null=True, blank=True)
    location = CharField(verbose_name="Место проведения", null=True, blank=True)
    department = ForeignKey(Department, verbose_name="Организатор", null=True, blank=True, on_delete=CASCADE)

    def __str__(self):
        return f"{self.name}"


class OlympiadParticipation(CommonObject):
    olympiad = ForeignKey(Olympiad, verbose_name="Олимпиада", on_delete=CASCADE)
    person = ForeignKey(User, verbose_name="Участник", on_delete=CASCADE)

    date = DateField(verbose_name="Дата участия", null=True, blank=True )
    award = CharField(verbose_name="Награда", null=True, blank=True)
    team_member = BooleanField(verbose_name="В составе команды", default=False)

    def __str__(self):
        return f"{self.olympiad}: {self.person}"
