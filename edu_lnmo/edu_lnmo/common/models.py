from django.db.models import *


class Organization(Model):
    name = CharField(verbose_name="Название", max_length=255)


class Department(Model):
    organization    = ForeignKey(Organization, on_delete=CASCADE)

    name            = CharField(verbose_name="Название", max_length=255)