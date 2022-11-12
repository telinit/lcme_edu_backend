#!/bin/bash

python ./edu_lnmo/manage.py shell -c "from edu_lnmo.imports.courses import *; CoursesDataImporter().do_import(open(\"teachers.csv\").read()).save_report(\"teachers_report.csv\")"