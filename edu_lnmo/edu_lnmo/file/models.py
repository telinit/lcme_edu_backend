from django.db.models import *

from ..user.models import User


class File(Model):
    name        = CharField(max_length=255, verbose_name="Название")
    owner       = ForeignKey(User, verbose_name="Владелец", on_delete=CASCADE)
    hash        = CharField(max_length = 64, blank = False, unique=True, verbose_name = "Хеш файла")
    size        = IntegerField(verbose_name="Размер")
    mime_type   = CharField(max_length=255, verbose_name="MIME-тип")
    data        = FileField(verbose_name="Содержимое")
