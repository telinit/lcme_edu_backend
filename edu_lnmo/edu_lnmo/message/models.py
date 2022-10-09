from django.db.models import *

from ..common.models import CommonObject
from ..file.models import File
from ..user.models import User


class MessageContent(CommonObject):
    class Meta:
        abstract = True

    body        = TextField(blank=True)
    attachments = ManyToManyField(File, verbose_name="Вложения", related_name="messages", blank=True)


class Message(MessageContent):
    sender  = ForeignKey(User, verbose_name="Отправитель", related_name="messages_sent", on_delete=CASCADE)
    sent_at = DateTimeField(verbose_name="Отправлено в")

    def __str__(self):
        b = str(self.body)
        b = b[0:max(20, len(b))]
        return f"{self.sender}: {b}"


class MessagePrivate(Message):
    receiver    = ForeignKey(User, verbose_name="Получатель", related_name="messages_received", on_delete=CASCADE)

    def __str__(self):
        return f"{self.sent_at}: {self.sender} -> {self.receiver}"


class MessageTaskSubmission(MessagePrivate):
    activity = ForeignKey("Activity", verbose_name="Задание", related_name="submissions", on_delete=CASCADE)


class MessageNews(Message):
    pass
