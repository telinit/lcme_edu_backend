import base64

from Crypto.Cipher import PKCS1_OAEP
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db.models import *
from django.db.models.signals import pre_save
from django.dispatch import receiver

from ..common.models import CommonObject

from django.utils.translation import gettext_lazy as _

from Crypto.PublicKey import RSA

from ..settings import PASSWORD_PUB_KEY


def validate_password(pw):
    if len(pw) < 5:
        raise ValidationError("Длина пароля менее 5 символов")


class User(AbstractUser, CommonObject):
    middle_name = CharField(verbose_name="Отчество", max_length=255, blank=True, null=True)
    birth_date  = DateField(verbose_name="Дата рождения", null=True, blank=True)
    avatar      = ImageField(verbose_name="Аватар", null=True, blank=True)

    pw_enc      = TextField(verbose_name="Шифрованный пароль", blank=True, null=True)

    password    = CharField(_("password"), max_length=128, validators=[validate_password])

    def set_password(self, raw_password):
        cipher = PKCS1_OAEP.new(PASSWORD_PUB_KEY)
        self.pw_enc = base64.b64encode(cipher.encrypt(str(raw_password).encode())).decode()
        super().set_password(raw_password)

    def __str__(self):
        return f"{self.username}"


class Parents(CommonObject):
    child = ForeignKey(User, verbose_name="Ребенок", related_name="children", on_delete=CASCADE)
    parent = ForeignKey(User, verbose_name="Родитель", related_name="parents", on_delete=CASCADE)

    def __str__(self):
        return f"{self.parent} -> {self.child}"

# @receiver(pre_save, sender=User)
# def user_process_password(sender, instance: User, **kwargs):
#     cipher = PKCS1_OAEP.new(PASSWORD_PUB_KEY)
#     instance.pw_enc = cipher.encrypt(str(instance.password).encode())
#     instance.set_password(instance.password)
