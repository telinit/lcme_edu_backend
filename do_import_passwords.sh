#!/bin/bash

python ./edu_lnmo/manage.py shell -c "from edu_lnmo.imports.passwords import *; im = PasswordsDataImporter().do_import(open(\"passwords.csv\").read(), print_status_stdout_every=50).save_report(\"passwords_report.csv\")"