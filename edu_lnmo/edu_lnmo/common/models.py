import uuid

from django.db.models import *
from django.db.models.manager import BaseManager


class CommonObject(Model):
    class Meta:
        abstract = True

    id = UUIDField(primary_key=True, null=False, default=uuid.uuid4)

    objects: QuerySet


class Organization(CommonObject):
    name = CharField(verbose_name="Название", max_length=255)
    name_short = CharField(verbose_name="Короткое название", max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.name_short}"


class Department(CommonObject):
    organization    = ForeignKey(Organization, on_delete=CASCADE)

    name            = CharField(verbose_name="Название", max_length=255)

    def __str__(self):
        return f"{self.organization}: {self.name}"