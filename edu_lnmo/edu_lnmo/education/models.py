from django.db.models import *

from ..common.models import Department
from ..user.models import User


class EducationSpecialization(Model):
    name        = CharField(max_length=255, verbose_name="Название")
    department  = ForeignKey(Department, verbose_name="Подразделение учебного заведения", on_delete=CASCADE)


class Education(Model):
    student         = ForeignKey(User, verbose_name="Учащийся", on_delete=CASCADE)

    started         = DateField(verbose_name="Дата поступления")
    finished        = DateField(verbose_name="Дата завершения", null=True)

    starting_class  = IntegerField(verbose_name="Класс поступления")
    finishing_class = IntegerField(verbose_name="Класс завершения")

    #department      = ForeignKey(Department, verbose_name="Подразделение")
    specialization  = ForeignKey(EducationSpecialization, verbose_name="Направление обучения", on_delete=CASCADE)