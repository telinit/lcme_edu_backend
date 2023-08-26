from typing import Any

from django.db.models import *
from django.db.models import CharField, IntegerField

from ..common.models import CommonObject
from ..user.models import User


class File(CommonObject):
    name        = CharField(max_length=255, verbose_name="Название")
    hash        = CharField(max_length = 64, blank = False, unique=True, verbose_name = "Хеш файла")
    size        = IntegerField(verbose_name="Размер")
    mime_type   = CharField(max_length=255, verbose_name="MIME-тип")

    owner = ForeignKey(to=User, verbose_name="Владелец", blank=True, null=True, on_delete=SET_NULL, related_name="files")
    parent = ForeignKey(to="File", verbose_name="Каталог", blank=True, null=True, on_delete=SET_NULL, related_name="children")

    def __str__(self):
        return f"{self.name} ({self.mime_type}, {self.size})"

    class Meta:
        verbose_name = "Файл"
        verbose_name_plural = "Файлы"

        indexes = [
            Index(fields=['name']),
            Index(fields=['hash']),
            Index(fields=['size']),
            Index(fields=['mime_type']),
            Index(fields=['owner']),
            Index(fields=['parent']),
        ]


