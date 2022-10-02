from django.db.models import *

from ..common.models import CommonObject
from ..course.models import Course
from ..file.models import File
from ..message.models import MessageContent


class Activity(CommonObject):
    course              = ForeignKey(Course, verbose_name="Курс", on_delete=CASCADE)

    title               = CharField(max_length=255, verbose_name="Название", blank=False)
    keywords            = CharField(max_length=255, verbose_name="Кодовое название", blank=True)

    is_hidden           = BooleanField(verbose_name="Скрыта", default=False)
    marks_limit         = IntegerField(verbose_name="Лимит оценок", default=1)

    order               = IntegerField(verbose_name="Номер в списке курса")
    date                = DateField(verbose_name="Дата проведения", blank=True, null=True)
    group               = CharField(max_length=255, verbose_name="Группа", blank=True, null=True)

    def __str__(self):
        return f"{self.course}: {self.order}. {self.title}"


class ActivityArticle(Activity, MessageContent):
    pass


class ActivityTask(Activity, MessageContent):
    due_date = DateTimeField(verbose_name="Срок сдачи", null=True)


class ActivityLink(Activity):
    link    = URLField(verbose_name="Ссылка")
    embed   = BooleanField(default=True, verbose_name="Встроена")


class ActivityMedia(Activity):
    file = ForeignKey(File, verbose_name="Файл", on_delete=CASCADE)