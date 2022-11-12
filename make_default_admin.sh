#!/bin/bash

cd edu_lnmo

./manage.py shell << EOF
from edu_lnmo.user.models import User;
u=User();
u.username="admin";
u.set_password("admin");
u.is_staff=True;
u.is_superuser=True;
u.first_name="Администратор"
u.save()
EOF
