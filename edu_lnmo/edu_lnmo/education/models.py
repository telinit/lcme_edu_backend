import datetime
import re
from re import Match
from typing import Any, Optional

from django.db.models import *
from django.db.models import ForeignKey, DateField, CharField

from ..common.models import CommonObject
from ..user.models import User


class EducationSpecialization(CommonObject):
    name        = CharField(max_length=255, verbose_name="Название")
    department  = ForeignKey("Department", verbose_name="Подразделение учебного заведения", on_delete=CASCADE)

    def __str__(self):
        return f"{self.department}: {self.name}"

    class Meta:
        verbose_name = "Направление обучения"
        verbose_name_plural = "Направления обучения"

        indexes = [
            Index(fields=['name']),
            Index(fields=['department'])
        ]


class Education(CommonObject):
    student         = ForeignKey(User, verbose_name="Учащийся", related_name="education", on_delete=CASCADE)

    started         = DateField(verbose_name="Дата поступления")
    finished        = DateField(verbose_name="Дата завершения", null=True, blank=True)

    starting_class  = CharField(max_length=10, verbose_name="Класс поступления")
    finishing_class = CharField(max_length=10, verbose_name="Класс завершения", null=True, blank=True)

    #department      = ForeignKey(Department, verbose_name="Подразделение")
    specialization  = ForeignKey(
        EducationSpecialization,
        verbose_name="Направление обучения",
        related_name="educations",
        on_delete=CASCADE
    )

    class Meta:
        verbose_name = "Обучение"
        verbose_name_plural = "Обучения"

        indexes = [
            Index(fields=['student']),
            Index(fields=['started']),
            Index(fields=['finished']),
            Index(fields=['starting_class']),
            Index(fields=['finishing_class']),
            Index(fields=['specialization'])
        ]

    def __str__(self):
        return f"{self.student}: {self.started} ({self.starting_class}) - {self.finished} ({self.finishing_class})"

    def get_current_class(self) -> str:
        def get_edu_year(date):
            if date.month > 8:
                return date.year
            else:
                return date.year - 1

        today = datetime.date.today()
        y_diff = get_edu_year(today) - get_edu_year(self.started)

        m: Optional[Match[str]] = re.match(r"(\d+)(.*)", self.starting_class)

        if not m:
            return str(5 + y_diff)
        else:
            return str(int(m[1]) + y_diff) + m[2]