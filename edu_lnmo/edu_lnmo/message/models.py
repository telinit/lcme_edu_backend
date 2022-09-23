from django.db.models import *

# from ..activity.models import ActivityTask
from ..file.models import File
from ..user.models import User


class MessageContent(Model):
    class Meta:
        abstract = True

    body        = TextField()
    attachments = ManyToManyField(File, verbose_name="Вложения")


class Message(MessageContent):
    sender  = ForeignKey(User, verbose_name="Отправитель", on_delete=CASCADE)
    sent_at = DateTimeField(verbose_name="Отправлено в")


class MessagePrivate(Message):
    receiver    = ForeignKey(User, verbose_name="Получатель", on_delete=CASCADE)
    is_read     = BooleanField(verbose_name="Прочитано")


class MessageTaskSubmission(MessagePrivate):
    activity = ForeignKey("ActivityTask", verbose_name="Задание", on_delete=CASCADE)


class MessageNews(Message):
    pass
