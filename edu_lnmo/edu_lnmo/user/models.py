import base64
from typing import Any

from Crypto.Cipher import PKCS1_OAEP
from django.contrib.auth.models import AbstractUser, UserManager
from django.core.exceptions import ValidationError
from django.db.models import *
from django.db.models import CharField, DateField, ImageField, TextField, ManyToManyField, ForeignKey
from django.db.models.signals import pre_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token

from ..common.models import CommonObject

from django.utils.translation import gettext_lazy as _

from Crypto.PublicKey import RSA

from ..settings import PASSWORD_PUB_KEY, AUTH_USER_MODEL, FILE_QUOTA_BASE


def validate_password(pw):
    if len(pw) < 5:
        raise ValidationError("Длина пароля менее 5 символов")


class User(AbstractUser, CommonObject):
    middle_name = CharField(verbose_name="Отчество", max_length=255, blank=True, null=True)
    birth_date  = DateField(verbose_name="Дата рождения", null=True, blank=True)
    avatar: ImageField      = ImageField(verbose_name="Аватар", null=True, blank=True)

    pw_enc      = TextField(verbose_name="Шифрованный пароль", blank=True, null=True)

    password    = CharField(_("password"), max_length=128, validators=[validate_password])

    children    = ManyToManyField("User", related_name="parents", verbose_name="Дети", blank=True)

    file_quota  = IntegerField(verbose_name="Квота на файлы", blank=True, null=True, default=FILE_QUOTA_BASE)

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

        indexes = [
            Index(fields=['last_name']),
            Index(fields=['first_name']),
            Index(fields=['middle_name']),
            Index(fields=['birth_date'])
        ]

    def set_password(self, raw_password):
        cipher = PKCS1_OAEP.new(PASSWORD_PUB_KEY)
        self.pw_enc = base64.b64encode(cipher.encrypt(str(raw_password).encode())).decode()
        super().set_password(raw_password)

    def full_name(self):
        return f"{self.last_name} {self.first_name} {self.middle_name}"

    @property
    def roles(self) -> list[str]:
        res = []

        if self.children.count() > 0:
            res += ["parent"]

        if self.enrollments.filter(finished_on=None, role = "s").count() > 0:
            res += ["student"]

        if self.enrollments.filter(finished_on=None, role="t").count() > 0:
            res += ["teacher"]

        if self.is_staff:
            res += ["staff"]

        if self.is_superuser:
            res += ["admin"]

        return res

    def __str__(self):
        return f"{self.username}"


class MultiToken(Token):
    user = ForeignKey(  # type: ignore[assignment]
        AUTH_USER_MODEL, related_name='tokens',
        on_delete=CASCADE, verbose_name=_("User")
    )

    class Meta:
        verbose_name = "Токен"
        verbose_name_plural = "Токены"

        indexes = [
            Index(fields=['user']),
            Index(fields=['key']),
            Index(fields=['created'])
        ]