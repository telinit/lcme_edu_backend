import random
from typing import Tuple

from django.db.models import Q
from transliterate import translit

from ..education.models import Education
from ..user.models import User


def generate_username(first_name: str, middle_name: str, last_name: str) -> str:
    t = lambda s: translit(s, 'ru', reversed=True)
    f = t(first_name[0]) if first_name else "_"
    m = t(middle_name[0]) if middle_name else "_"
    l = t(last_name) if last_name else "_"
    return f"{f}{m}{l}".replace("'", "")


def create_user(first_name: str, middle_name: str, last_name: str) -> Tuple[User, bool]:
    user = User.objects.filter(
        last_name=last_name,
        first_name=first_name,
        middle_name=middle_name
    )

    if not user:
        username_base = generate_username(first_name, middle_name, last_name)
        usernames = User.objects.filter(username__startswith=username_base).values_list("username", flat=True)
        username_new = username_base
        i = 1
        while username_new in usernames:
            i += 1
            username_new = username_base + str(i)

        user, _ = User.objects.get_or_create(
            last_name=last_name,
            first_name=first_name,
            middle_name=middle_name,
            username=username_new
        )
        created = True
    else:
        user = user[0]
        created = False

    return user, created


def generate_password(length=8) -> str:
    alph = "0123456789"
    return "".join([random.choice(alph) for _ in range(length)])


def generate_passwords_for_users():
    csv = []
    csv += [['Фамилия', 'Имя', 'Отчество', 'Логин', 'Пароль']]

    q1 = Q(password__isnull=True)
    q2 = Q(password="")

    for user in User.objects.filter(q1 | q2):
        pw = generate_password()
        user.set_password(pw)
        user.save()
        csv += [[user.last_name, user.first_name, user.middle_name, user.username, pw]]

    return csv
