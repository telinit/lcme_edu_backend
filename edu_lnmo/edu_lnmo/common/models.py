import uuid

from django.db.models import *


class CommonObject(Model):
    class Meta:
        abstract = True

    id = UUIDField(primary_key=True, null=False, default=uuid.uuid4)


class Organization(CommonObject):
    name = CharField(verbose_name="Название", max_length=255)

    def __str__(self):
        return f"{self.name}"


class Department(CommonObject):
    organization    = ForeignKey(Organization, on_delete=CASCADE)

    name            = CharField(verbose_name="Название", max_length=255)

    def __str__(self):
        return f"{self.organization}: {self.name}"