import uuid

from django.contrib.auth.models import AbstractUser
from django.db.models import *


class User(AbstractUser):
    id = UUIDField(primary_key=True, null=False, default=uuid.uuid4)

    middle_name = CharField(verbose_name="Отчество", max_length=255)
    birth_date  = DateField(null=True, blank=True, verbose_name="Дата рождения")
    avatar      = ImageField(verbose_name="Аватар")

    parents     = ManyToManyField("self", verbose_name="Родители")  # , related_name="parents"

    def __str__(self):
        return f"{self.last_name} {self.first_name} {self.middle_name}"