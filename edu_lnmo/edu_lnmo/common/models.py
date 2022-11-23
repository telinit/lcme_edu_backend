import uuid

from django.contrib.auth.models import Group
from django.db.models import *
from django.db.models.manager import BaseManager


class CommonObject(Model):
    class Meta:
        abstract = True
        verbose_name = "Объект"
        verbose_name_plural = "Объекты"

    id = UUIDField(primary_key=True, null=False, default=uuid.uuid4)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)

    objects: QuerySet


class Permission(Model):
    invert_condition = BooleanField(verbose_name="Инвертировать условие", default=False)
    do_allow = BooleanField(verbose_name="Разрешить доступ (или запретить)", default=False)

    user  = ForeignKey(
        to="User", related_name="direct_permissions", verbose_name="Пользователь",
        blank=True, null=True,
        on_delete=CASCADE)
    group = ForeignKey(
        to=Group, related_name="direct_permissions", verbose_name="Группа пользователей",
        blank=True, null=True,
        on_delete=CASCADE
    )
    for_class = CharField(verbose_name="Класс", max_length=255, blank=True, null=True)
    spec = ForeignKey(
        to="EducationSpecialization", related_name="direct_permissions", verbose_name="Направление обучения",
        blank=True, null=True,
        on_delete=CASCADE
    )
    role = CharField(verbose_name="Роль", max_length=255, blank=True, null=True )

    class Meta:
        verbose_name = "Право доступа"
        verbose_name_plural = "Права доступа"


class Organization(CommonObject):
    name = CharField(verbose_name="Название", max_length=255)
    name_short = CharField(verbose_name="Короткое название", max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.name_short}"

    class Meta:
        verbose_name = "Организация"
        verbose_name_plural = "Организации"


class Department(CommonObject):
    organization    = ForeignKey(Organization, on_delete=CASCADE)

    name            = CharField(verbose_name="Название", max_length=255)

    def __str__(self):
        return f"{self.organization}: {self.name}"

    class Meta:
        verbose_name = "Отдел"
        verbose_name_plural = "Отделы"