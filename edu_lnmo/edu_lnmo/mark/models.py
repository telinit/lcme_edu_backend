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

    def __str__(self):
        return f"{self.student}: {self.activity}: {self.value}"
