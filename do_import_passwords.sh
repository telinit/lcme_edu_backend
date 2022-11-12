#!/bin/bash

cd edu_lnmo

python manage.py shell -c "from edu_lnmo.imports.passwords import *; im = PasswordsDataImporter().do_import(open(\"passwords.csv\").read()).save_report(\"passwords_report.csv\")"