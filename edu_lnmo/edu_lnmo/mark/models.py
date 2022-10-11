from django.db.models import *

from ..activity.models import Activity
from ..common.models import CommonObject
from ..course.models import Course
from ..user.models import User


class Mark(CommonObject):
    teacher = ForeignKey(User, verbose_name="Преподаватель", related_name="teacher", on_delete=CASCADE)
    student = ForeignKey(User, verbose_name="Учащийся", related_name="student", on_delete=CASCADE)
    value   = CharField(max_length=255, verbose_name="Значение", blank=False, null=False)
    comment = TextField(verbose_name="Коментарий", blank=True)

    activity = ForeignKey(Activity, verbose_name="Активность", related_name="marks", on_delete=CASCADE)
    course = ForeignKey(Course, verbose_name="Курс", related_name="marks", on_delete=CASCADE)

    class FinalType(TextChoices):
        Q1 = 'Q1', "1 четверть"
        Q2 = 'Q2', "2 четверть"
        Q3 = 'Q3', "3 четверть"
        Q4 = 'Q4', "4 четверть"
        H1 = 'H1', "1 полугодие"
        H2 = 'H2', "2 полугодие"
        Y = 'Y', "Годовая"
        E = 'E', "Экзамен"
        F = 'F', "Итоговая"

    final_type = CharField(
        choices=FinalType.choices,
        default=FinalType.F,
        max_length=2,
        null=True,
        blank=True
    )

    def __str__(self):
        fin = f", {FinalType[self.final_type].label}" if self.final_type else ""
        return f"{self.student}: {self.activity or self.course} ({self.value}{fin})"