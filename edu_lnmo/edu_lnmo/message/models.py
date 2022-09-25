from django.db.models import *
from polymorphic.models import PolymorphicModel

# from ..activity.models import ActivityTask
from ..file.models import File
from ..user.models import User


class MessageContent(PolymorphicModel):
    class Meta:
        abstract = True

    body        = TextField(blank=True)
    attachments = ManyToManyField(File, verbose_name="Вложения")


class Message(MessageContent):
    sender  = ForeignKey(User, verbose_name="Отправитель", on_delete=CASCADE)
    sent_at = DateTimeField(verbose_name="Отправлено в")

    def __str__(self):
        b = str(self.body)
        b = b[0:max(20, len(b))]
        return f"{self.sender}: {b}"


class MessagePrivate(Message):
    receiver    = ForeignKey(User, verbose_name="Получатель", on_delete=CASCADE)
    is_read     = BooleanField(verbose_name="Прочитано")

    def __str__(self):
        return f"{self.sent_at}: {self.sender} -> {self.receiver}"


class MessageTaskSubmission(MessagePrivate):
    activity = ForeignKey("ActivityTask", verbose_name="Задание", on_delete=CASCADE)


class MessageNews(Message):
    pass
