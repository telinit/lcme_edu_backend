#!/bin/bash

python ./edu_lnmo/manage.py shell -c "from edu_lnmo.imports.passwords import *; im = PasswordsDataImporter().do_import(open(\"passwords.csv\").read()).save_report(\"passwords_report.csv\")"