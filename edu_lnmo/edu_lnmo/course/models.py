from django.db.models import *

from ..user.models import User


class Course(Model):
    title       = CharField(max_length=255, verbose_name="Название")
    description = TextField(verbose_name="Описание")

    # public = BooleanField(verbose_name="Публичный")
    teachers    = ManyToManyField(User, related_name="teachers", verbose_name="Преподаватели", blank=True)
    students    = ManyToManyField(User, related_name="students", verbose_name="Учащиеся", blank=True)

    def __str__(self):
        return f"{self.title}"