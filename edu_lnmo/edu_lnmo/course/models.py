from django.db.models import *

from ..file.models import File
from ..user.models import User


class Course(Model):
    title       = CharField(max_length=255, verbose_name="Название", blank=False)
    description = TextField(verbose_name="Описание")

    logo        = ForeignKey(File, related_name="logo", verbose_name="Логотип", null=True, on_delete=SET_NULL)
    cover       = ForeignKey(File, related_name="cover", verbose_name="Обложка", null=True, on_delete=SET_NULL)

    # public = BooleanField(verbose_name="Публичный")
    teachers    = ManyToManyField(User, related_name="teachers", verbose_name="Преподаватели", blank=True)
    students    = ManyToManyField(User, related_name="students", verbose_name="Учащиеся", blank=True)

    def __str__(self):
        return f"{self.title}"

    def user_has_permissions(self, uid: str, read: bool = False, write: bool = False) -> bool:
        u = User(pk=uid)

        t = self.teachers.contains(u)
        if write and not t:
            return False

        s = self.students.contains(u)
        if read and not (s or t):
            return False

        return True
