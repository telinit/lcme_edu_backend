import uuid

from django.db.models import *

from ..common.models import CommonObject, Department
from ..course.models import Course
from ..file.models import File
from ..user.models import User


class Olympiad(CommonObject):
    name = CharField(verbose_name="Название", max_length=512, null=False, blank=False)
    category = CharField(verbose_name="Предметная область", max_length=255, null=False, blank=False)
    website = URLField(verbose_name="Сайт олимпиады", null=True, blank=True)
    organization = CharField(verbose_name="Организатор", max_length=512, null=True, blank=True)
    department = ForeignKey(Department, verbose_name="Подразделение", null=True, blank=True, on_delete=SET_NULL)
    logo = ForeignKey(File, verbose_name="Логотип", null=True, blank=True, on_delete=SET_NULL)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = "Олимпиада"
        verbose_name_plural = "Олимпиады"

        indexes = [
            Index(fields=['name']),
            Index(fields=['category']),
            Index(fields=['logo']),
            Index(fields=['organization']),
            Index(fields=['department']),
        ]


class OlympiadParticipation(CommonObject):
    olympiad = ForeignKey(Olympiad, verbose_name="Олимпиада", on_delete=CASCADE)
    person = ForeignKey(User, verbose_name="Участник", on_delete=CASCADE)

    date = DateTimeField(verbose_name="Дата участия", null=True, blank=True )
    award = CharField(verbose_name="Награда", max_length=512, null=True, blank=True)
    team_member = BooleanField(verbose_name="В составе команды", default=False)
    stage = CharField("Этап олимпиады", max_length=255, null=True)
    location = CharField(verbose_name="Место проведения", max_length=512, null=True, blank=True)

    def __str__(self):
        return f"{self.olympiad}: {self.person}"

    class Meta:
        verbose_name = "Участие в олимпиаде"
        verbose_name_plural = "Участия в олимпиадах"

        indexes = [
            Index(fields=['olympiad']),
            Index(fields=['person']),
            Index(fields=['date']),
            Index(fields=['award']),
            Index(fields=['team_member']),
            Index(fields=['stage']),
            Index(fields=['location']),
        ]
