import datetime
from csv import DictReader
from typing import Optional

from django.db.models import Max, Q

from .base import CSVDataImporter
from ..activity.models import Activity
from ..course.models import Course


class ActivitiesImportResult(object):
    objects = []
    report_rows = [["Номер", "Тип объекта", "Тема"]]

    def save_report(self, file_name: str):
        open(file_name, "w").writelines(map(lambda ws: ",".join(ws) + "\n", self.report_rows))


class ActivitiesDataImporter(CSVDataImporter):
    def parse_date(self, s: str) -> Optional[datetime.date]:
        try:
            l = [*map(int, s.split("."))]
            return datetime.date(l[2], l[1], l[0])
        except:
            return None

    def do_import(self, data: str, course_id, sep=","):
        r = DictReader(data.splitlines(), delimiter=sep)
        res = ActivitiesImportResult()

        course = Course.objects.get(id=course_id)

        i = 1 + (Activity.objects.filter(course=course).aggregate(Max('order'))['order__max'] or 0)

        for old_rec in r:
            rec = dict()
            all_empty = True
            for k in old_rec:
                all_empty &= (str(old_rec[k]).strip() == "")
                rec[str(k).strip().capitalize()] = old_rec[k]

            if all_empty:
                continue

            act, _ = Activity.objects.get_or_create(
                content_type = Activity.ActivityContentType.GEN,
                course = course,
                title = rec["Тема"].strip(),
                keywords = rec["Ключевое слово"].strip(),
                lesson_type = rec["Форма занятия"].strip(),
                is_hidden = False,
                marks_limit = int(rec["Количество оценок"].strip()),
                hours=int(rec["Часы"].strip()),
                fgos_complient = str(rec["Фгос"]).strip().lower() == "да",
                order = i,
                date = self.parse_date(rec["Дата"].strip()),
                group = rec["Раздел"].strip(),
                scientific_topic = rec["Раздел научной дисциплины"].strip()
            )
            res.objects += [act]
            res.report_rows += [[str(i), "Тема", rec["Тема"].strip()]]
            i += 1

            hw = rec["Домашнее задание"].strip()
            if hw != "":
                act_hw, _ = Activity.objects.get_or_create(
                    content_type=Activity.ActivityContentType.TSK,
                    course=course,
                    title=f"Домашнее задание",
                    keywords=rec["Ключевое слово"].strip(),
                    lesson_type="Домашняя работа",
                    is_hidden=False,
                    marks_limit=int(rec["Количество оценок"].strip()),
                    hours=1,
                    fgos_complient=str(rec["Фгос"]).strip().lower() == "да",
                    order=i,
                    date=self.parse_date(rec["Дата"].strip()),
                    group=rec["Раздел"].strip(),
                    scientific_topic=rec["Раздел научной дисциплины"].strip(),
                    body=hw,
                    linked_activity=act
                )
                res.objects += [act_hw]
                res.report_rows += [[str(i), "Домашнее задание", rec["Тема"].strip()]]
                i += 1

            refs = rec["Материалы урока"].strip()
            if refs != "":
                act_refs, _ = Activity.objects.get_or_create(
                    content_type=Activity.ActivityContentType.TXT,
                    course=course,
                    title=f"Материалы урока",
                    keywords=rec["Ключевое слово"].strip(),
                    is_hidden=False,
                    fgos_complient=str(rec["Фгос"]).strip().lower() == "да",
                    order=i,
                    date=self.parse_date(rec["Дата"].strip()),
                    group=rec["Раздел"].strip(),
                    scientific_topic=rec["Раздел научной дисциплины"].strip(),
                    body=refs,
                    linked_activity=act,
                    marks_limit=0
                )
                res.objects += [act_refs]
                res.report_rows += [[str(i), "Материалы урока", rec["Тема"].strip()]]
                i += 1

        return res