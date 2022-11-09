
class ActivitiesImportResult(object):
    objects = []
    report_rows = [["Фамилия","Имя","Отчество","Логин","Пароль"]]

    def save_report(self, file_name: str):
        open(file_name, "w").writelines(map(lambda ws: ",".join(ws) + "\n", self.report_rows))


class ActivitiesDataImporter(CSVDataImporter):
    def do_import(self, data: str):
        r = DictReader(data.splitlines())
        res = ActivitiesImportResult()
        users = {}
        for rec in r: