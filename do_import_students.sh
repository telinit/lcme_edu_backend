#!/bin/bash

python ./edu_lnmo/manage.py shell -c "from edu_lnmo.imports.students import *; im = StudentsDataImporter().do_import(open(\"students.csv\").read()).save_report(\"students_report.csv\")"