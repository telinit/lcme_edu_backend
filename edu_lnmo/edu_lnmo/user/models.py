from django.contrib.auth.models import AbstractUser
from django.db.models import *

from ..common.models import CommonObject


class User(AbstractUser, CommonObject):
    middle_name = CharField(verbose_name="Отчество", max_length=255)
    birth_date  = DateField(null=True, blank=True, verbose_name="Дата рождения")
    avatar      = ImageField(verbose_name="Аватар")

    parents     = ManyToManyField("self", verbose_name="Родители", blank=True)  # , related_name="parents"

    def __str__(self):
        return f"{self.username}"