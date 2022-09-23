from django.db.models import *

from ..course.models import Course
from ..file.models import File
from ..message.models import MessageContent


class Activity(Model):
    course      = ForeignKey(Course, verbose_name="Курс", on_delete=CASCADE)

    title       = CharField(max_length=255, verbose_name="Название")

    is_hidden   = BooleanField(verbose_name="Скрыта")
    is_markable = BooleanField(verbose_name="Оцениваемая")

    order       = IntegerField(verbose_name="Номер в списке курса")

    def __str__(self):
        return f"{self.course}: {self.order}. {self.title}"


class ActivityBasic(Activity):
    pass


class ActivityArticle(Activity, MessageContent):
    pass


class ActivityTask(Activity, MessageContent):
    due_date = DateTimeField(verbose_name="Срок сдачи", null=True)


class ActivityLink(Activity):
    link    = URLField(verbose_name="Ссылка")
    embed   = BooleanField(default=True, verbose_name="Встроено")


class ActivityMedia(Activity):
    file = ForeignKey(File, verbose_name="Файл", on_delete=CASCADE)


class ActivityGroup(Activity):
    children = ManyToManyField(Activity, related_name="children")