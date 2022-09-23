#!/bin/bash

rm -rv edu_lnmo/migrations db.sqlite3
./manage.py makemigrations edu_lnmo
./manage.py migrate
echo 'from edu_lnmo.user.models import User;u=User();u.username="admin";u.set_password("admin");u.is_staff=True;u.is_superuser=True;u.save()' | ./manage.py shell