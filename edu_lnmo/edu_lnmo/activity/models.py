from django.db.models import *

from ..common.models import CommonObject
from ..course.models import Course
from ..file.models import File


class Activity(CommonObject):
    class ActivityType(TextChoices):
        GEN  = 'GEN', "Общая" # TODO: Implement first
        ART  = 'ART', "Статья"
        TSK  = 'TSK', "Задание"
        LNK  = 'LNK', "Ссылка"
        MED  = 'MED', "Медиа-контент"
        FIN  = 'FIN', "Итоговый контроль"

    # TODO: Implement first
    type = CharField(choices=ActivityType.choices, default=ActivityType.GEN, max_length=3)

    course              = ForeignKey(Course, verbose_name="Курс", related_name="activities", on_delete=CASCADE)

    title               = CharField(max_length=255, verbose_name="Название", blank=False)
    keywords            = CharField(max_length=255, verbose_name="Кодовое название", blank=True)

    is_hidden           = BooleanField(verbose_name="Скрыта", default=False)
    marks_limit         = IntegerField(verbose_name="Лимит оценок", default=1)

    order               = IntegerField(verbose_name="Номер в списке курса")
    date                = DateField(verbose_name="Дата проведения")
    # TODO: Implement later
    group               = CharField(max_length=255, verbose_name="Группа", blank=True, null=True)

    body = TextField(blank=True)
    files = ManyToManyField(File, verbose_name="Вложения/файлы", related_name="activities", blank=True)

    due_date = DateTimeField(verbose_name="Срок сдачи", null=True, blank=True)

    link = URLField(verbose_name="Ссылка", null=True, blank=True)
    embed = BooleanField(default=True, verbose_name="Встроена")

    class FinalType(TextChoices):
        Q1 = 'Q1', "1 четверть"
        Q2 = 'Q2', "2 четверть"
        Q3 = 'Q3', "3 четверть"
        Q4 = 'Q4', "4 четверть"
        H1 = 'H1', "1 полугодие"
        H2 = 'H2', "2 полугодие"
        Y = 'Y', "Годовая"
        E = 'E', "Экзамен"
        F = 'F', "Итоговая"

    final_type = CharField(
        choices=FinalType.choices,
        default=FinalType.F,
        max_length=2,
        null=True,
        blank=True
    )

    def __str__(self):
        return f"{self.course}: {self.order}. {self.title}"
