from django.db.models import *

from ..common.models import CommonObject
from ..user.models import User


class UnreadObject(CommonObject):
    class ObjType(TextChoices):
        MSG  = 'MSG', "Сообщение"
        MRK  = 'MRK', "Оценка"
        CRS  = 'CRS', "Курс"
        ACT  = 'ACT', "Активность"
        NWS  = 'NWS', "Новость"
        EDU  = 'EDU', "Обучение"
        FLE  = 'FLE', "Файл"
        FRM   = 'FRM', "Форум"
        TSK   = 'TSK', "Задание"
        UNK   = 'UNK', "Другое"

    obj = UUIDField(verbose_name="Объект", null=False)
    type = CharField(verbose_name="Тип объекта", choices=ObjType.choices, default=ObjType.UNK, max_length=3)
    user = ForeignKey(User, verbose_name="Пользователь", on_delete=CASCADE)
    created = DateTimeField(verbose_name="Время")