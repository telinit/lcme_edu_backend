#!/bin/bash

cd edu_lnmo

python manage.py shell -c "from edu_lnmo.imports.students import *; im = StudentsDataImporter().do_import(open(\"students.csv\").read()).save_report(\"students_report.csv\")"