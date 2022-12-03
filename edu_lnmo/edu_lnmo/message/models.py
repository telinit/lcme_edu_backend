from django.db.models import *

from ..common.models import CommonObject
from ..file.models import File
from ..user.models import User


class Message(CommonObject):
    class MessageType(TextChoices):
        THR  = 'THR', "Тематическое"
        PRV  = 'PRV', "Личное"
        NEW  = 'NEW', "Новость"
        MAN  = 'MAN', "Справка"

    type = CharField(choices=MessageType.choices, max_length=3, default=MessageType.PRV)
    thread = ForeignKey("MessageThread", related_name="messages", verbose_name="Тема", blank=True, null=True, on_delete=SET_NULL)

    sender = ForeignKey(User, verbose_name="Отправитель", related_name="messages_sent", on_delete=CASCADE)
    receiver = ForeignKey(User, verbose_name="Получатель", related_name="messages_received", blank=True, null=True, on_delete=SET_NULL)

    body = TextField(blank=True)
    attachments = ManyToManyField(File, verbose_name="Вложения", related_name="messages", blank=True)

    manual_category = CharField(verbose_name="Раздел", max_length=255, blank=True, null=True)
    manual_audience = CharField(verbose_name="Предназначено для ролей", max_length=255, blank=True, null=True)

    class Meta:
        verbose_name = "Сообщение"
        verbose_name_plural = "Сообщения"

        indexes = [
            Index(fields=['type']),
            Index(fields=['thread']),
            Index(fields=['sender']),
            Index(fields=['receiver']),
            Index(fields=['manual_category']),
            Index(fields=['manual_audience'])
        ]

class MessageThread(CommonObject):
    class ThreadType(TextChoices):
        GRP = 'GRP', "Группа"
        FRM = 'FRM', "Форум"
        SUP = 'SUP', "Поддержка"

    class SupportStatus(TextChoices):
        OPEN = 'OPEN', "Открыт"
        CLOSED = 'CLOSED', "Закрыт"
        RESOLVED = 'RESOLVED', "Решен"
        REJECTED = 'REJECTED', "Отклонен"
        MORE_INFO = 'MORE_INFO', "Требуется уточнение"

    type = CharField(choices=ThreadType.choices, max_length=3)

    topic = CharField(verbose_name="Название темы", max_length=255, blank=True, null=True)
    members = ManyToManyField("User", verbose_name="Участники", blank=True)

    # forum_parent_thread   = ForeignKey("MessageThread", verbose_name="Родительская тема", blank=True, null=True, on_delete=CASCADE)
    # forum_user_subthreads = BooleanField(verbose_name="Разрешено создавать темы", blank=False, null=False, default=False)

    support_status = CharField(choices=SupportStatus.choices, blank=True, null=True, max_length=10)

    group = ForeignKey(to="ThreadGroup", verbose_name="Группа тем", related_name="threads", null=True, blank=True, on_delete=SET_NULL)

    class Meta:
        verbose_name = "Тема сообщений"
        verbose_name_plural = "Темы сообщений"

        indexes = [
            Index(fields=['type']),
            Index(fields=['topic']),
            Index(fields=['support_status']),
            Index(fields=['group'])
        ]

class ThreadGroup(CommonObject):
    name = CharField(verbose_name="Название", max_length=255, blank=False, null=False)

    parent = ForeignKey(to="ThreadGroup", verbose_name="Родительская группа", related_name="children", null=True, blank=True, on_delete=SET_NULL)

    class Meta:
        verbose_name = "Группа тем сообщений"
        verbose_name_plural = "Группы тем сообщений"

        indexes = [
            Index(fields=['name']),
            Index(fields=['parent'])
        ]
