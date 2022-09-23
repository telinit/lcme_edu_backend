from django.db.models import *


class Organization(Model):
    name = CharField(verbose_name="Название", max_length=255)

    def __str__(self):
        return f"{self.name}"


class Department(Model):
    organization    = ForeignKey(Organization, on_delete=CASCADE)

    name            = CharField(verbose_name="Название", max_length=255)

    def __str__(self):
        return f"{self.organization}: {self.name}"