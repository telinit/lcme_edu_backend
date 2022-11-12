#!/bin/sh

script_path=$(dirname $(readlink -f $0))

cd "$script_path/edu_lnmo"

sleep 10

python manage.py migrate
python manage.py runserver 0.0.0.0:8000 --insecure

