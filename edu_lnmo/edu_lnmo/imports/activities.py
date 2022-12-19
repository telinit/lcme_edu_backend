import datetime
from csv import DictReader
from typing import Optional

from django.db.models import Max, Q

from .base import CSVDataImporter
from ..activity.models import Activity
from ..course.models import Course


class ActivitiesImportResult(object):
    objects: list[object]
    report_rows: list[list[str]]

    def __init__(self):
        self.objects = []
        self.report_rows = [["Номер", "Тип объекта", "Тема"]]

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

        print(res.report_rows)

        course = Course.objects.get(id=course_id)

        order = 1 + (Activity.objects.filter(course=course).aggregate(Max('order'))['order__max'] or 0)
        i = 0

        for old_rec in r:
            try:
                rec = dict()
                all_empty = True
                for k in old_rec:
                    val_list_all_empty  =   isinstance(old_rec[k], list) and all(map(lambda x: not x, old_rec[k]))
                    val_empty           =   str(old_rec[k]).strip() == ""
                    all_empty           &=  val_list_all_empty or val_empty

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
                    order = order,
                    date = self.parse_date(rec["Дата"].strip()),
                    group = rec["Раздел"].strip(),
                    scientific_topic = rec["Раздел научной дисциплины"].strip(),
                    body = rec["Материалы урока"].strip()
                )
                res.objects += [act]
                res.report_rows += [[str(order), "Тема", rec["Тема"].strip()]]
                order += 1

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
                        order=order,
                        date=self.parse_date(rec["Дата"].strip()),
                        group=rec["Раздел"].strip(),
                        scientific_topic=rec["Раздел научной дисциплины"].strip(),
                        body=hw,
                        linked_activity=act
                    )
                    res.objects += [act_hw]
                    res.report_rows += [[str(order), "Домашнее задание", rec["Тема"].strip()]]
                    order += 1


                i += 1
            except Exception as e:
                raise Exception(f"Failed to import a record {i} ({old_rec}): {e}")

        return res
