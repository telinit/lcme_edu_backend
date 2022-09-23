from django.db.models import *

from ..activity.models import Activity
from ..user.models import User


class Mark(Model):
    teacher = ForeignKey(User, verbose_name="Преподаватель", related_name="teacher", on_delete=CASCADE)
    student = ForeignKey(User, verbose_name="Учащийся", related_name="student", on_delete=CASCADE)
    value   = CharField(max_length=255, verbose_name="Значение")
    comment = TextField(verbose_name="Коментарий", blank=True)

    def __str__(self):
        return f"{self.student}: {self.value}"


class MarkActivity(Mark):
    activity = ForeignKey(Activity, verbose_name="Активность", on_delete=CASCADE)

    def __str__(self):
        return f"{self.student}: {self.activity} ({self.value})"


class MarkDiscipline(Mark):
    pass


class MarkFinal(Mark):
    class FinalType(TextChoices):
        Q1  = 'Q1', "1 четверть"
        Q2  = 'Q2', "2 четверть"
        Q3  = 'Q3', "3 четверть"
        Q4  = 'Q4', "4 четверть"
        H1  = 'H1', "1 полугодие"
        H2  = 'H2', "2 полугодие"
        Y   = 'Y', "Годовая"
        F   = 'F', "Итоговая"

    final_type = CharField(choices=FinalType.choices, default=FinalType.F, max_length=2)
