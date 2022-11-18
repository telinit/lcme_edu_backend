#!/bin/bash

docker stop edu-dev-postgres
docker rm edu-dev-postgres
docker run -p 5432:5432 --name edu-dev-postgres -e POSTGRES_PASSWORD=postgres -d postgres
sleep 5
./manage.py makemigrations edu_lnmo
./manage.py migrate
./manage.py shell << EOF
from edu_lnmo.user.models import User;
u=User();
u.username="admin";
u.set_password("admin");
u.is_staff=True;
u.is_superuser=True;
u.first_name="Админ"
u.save()
EOF
