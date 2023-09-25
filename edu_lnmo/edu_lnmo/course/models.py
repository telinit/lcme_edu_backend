from typing import Any

from django.db.models import *
from django.db.models import ForeignKey, CharField, DateTimeField, TextField
from rest_framework.viewsets import ViewSet

from ..common.models import CommonObject
from ..education.models import EducationSpecialization
from ..file.models import File
from ..user.models import User


class Course(CommonObject):
    class CourseType(TextChoices):
        GEN = 'GEN', "Курс"
        EDU = 'EDU', "Учебная программа"
        SEM = 'SEM', "Семинар"
        CLB = 'CLB', "Кружок"
        ELE = 'ELE', "Предмет по выбору"
        ADM = 'ADM', "Вступительное испытание"

    class MarkingSystem(TextChoices):
        NOP = 'NOP', "Без оценивания"
        FVE = 'FVE', "5-бальная"
        HND = 'HND', "100-бальная"
        CST = 'CST', "Произвольная"

    type = CharField(choices=CourseType.choices, default=CourseType.GEN, max_length=3, null=False)
    marking = CharField(choices=MarkingSystem.choices, default=MarkingSystem.FVE, max_length=3, null=False)

    title = CharField(max_length=255, verbose_name="Название", blank=False)
    description = TextField(verbose_name="Описание", blank=True, null=True)

    for_class = CharField(max_length=10, verbose_name="Класс", blank=True)
    for_specialization = ForeignKey(
        EducationSpecialization,
        verbose_name="Направление обучения",
        related_name="courses",
        on_delete=SET_NULL,
        blank=True,
        null=True
    )
    for_group = CharField(verbose_name="Группа", max_length=255, null=True, blank=True)

    logo = ForeignKey(File, related_name="course_logos", verbose_name="Логотип", blank=True, null=True, on_delete=SET_NULL)
    cover = ForeignKey(File, related_name="course_covers", verbose_name="Обложка", blank=True, null=True, on_delete=SET_NULL)

    archived = DateTimeField(verbose_name="Дата архивирования", null=True, blank=True)

    def __str__(self):
        info = ", ".join([*filter(lambda x:x, [str(self.for_specialization), self.for_class, self.for_group])])
        return f"{self.title}" + (f" ({info})" if info else "")

    class Meta:
        verbose_name = "Курс"
        verbose_name_plural = "Курсы"

        indexes = [
            Index(fields=['type']),
            Index(fields=['title']),
            Index(fields=['for_class']),
            Index(fields=['for_specialization']),
            Index(fields=['for_group']),
            Index(fields=['logo']),
            Index(fields=['cover']),
            Index(fields=['marking']),
            Index(fields=['archived']),
        ]

    @property
    def teachers(self) -> QuerySet:
        return CourseEnrollment.objects.filter(
            course=self,
            finished_on=None,
            role=CourseEnrollment.EnrollmentRole.teacher
        )

    @property
    def students(self) -> QuerySet:
        return CourseEnrollment.objects.filter(
            course=self,
            finished_on=None,
            role=CourseEnrollment.EnrollmentRole.student
        )

    @property
    def managers(self) -> QuerySet:
        return CourseEnrollment.objects.filter(
            course=self,
            finished_on=None,
            role=CourseEnrollment.EnrollmentRole.manager
        )

    def user_has_permissions(self, uid: str, read: bool = False, write: bool = False) -> bool:
        u = User(pk=uid)

        t = self.teachers.contains(u)
        if write and not t:
            return False

        s = self.students.contains(u)
        if read and not (s or t):
            return False

        return True


class CourseEnrollment(CommonObject):
    class EnrollmentRole(TextChoices):
        teacher = 't', "Преподаватель"
        student = 's', "Учащийся"
        manager = 'm', "Менеджер"
        observer = 'o', "Наблюдатель"
        listener = 'l', "Вольный слушатель"

    person = ForeignKey(User, verbose_name="Пользователь", related_name="enrollments", on_delete=CASCADE)
    course = ForeignKey(Course, verbose_name="Курс", related_name="enrollments", on_delete=CASCADE)
    role = CharField(choices=EnrollmentRole.choices, max_length=3)
    finished_on = DateTimeField(verbose_name="Завершена", null=True, blank=True)

    def __str__(self):
        return f"{self.role}: {self.person.full_name()} -> {self.course}"

    class Meta:
        verbose_name = "Запись на курс"
        verbose_name_plural = "Записи на курсы"

        indexes = [
            Index(fields=['person']),
            Index(fields=['course']),
            Index(fields=['role']),
            Index(fields=['finished_on'])
        ]

    @classmethod
    def get_courses_of_teacher(cls, user) -> QuerySet:
        return Course.objects.filter(
            enrollments__role=cls.EnrollmentRole.teacher,
            enrollments__finished_on__isnull=True,
            enrollments__person=user
        )

    @classmethod
    def get_courses_of_student(cls, user: User | QuerySet) -> QuerySet:
        if isinstance(user, User):
            return Course.objects.filter(
                enrollments__role=cls.EnrollmentRole.student,
                enrollments__finished_on__isnull=True,
                enrollments__person=user
            )
        elif isinstance(user, QuerySet):
            return Course.objects.filter(
                enrollments__role=cls.EnrollmentRole.student,
                enrollments__finished_on__isnull=True,
                enrollments__person__in=user
            )
        else:
            raise TypeError()


    @staticmethod
    def get_courses_of_user(user: User | QuerySet) -> QuerySet:
        if isinstance(user, User):
            return Course.objects.filter(
                enrollments__finished_on__isnull=True,
                enrollments__person=user
            )
        elif isinstance(user, QuerySet):
            return Course.objects.filter(
                enrollments__finished_on__isnull=True,
                enrollments__person__in=user
            )
        else:
            raise TypeError()

    @classmethod
    def get_students_of_courses(cls, courses, **more_user_filters):
        return User.objects.filter(
            enrollments__person=F("id"),
            enrollments__role=cls.EnrollmentRole.student,
            enrollments__course__in=courses,
            enrollments__finished_on__isnull=True,
            **more_user_filters
        )

    @classmethod
    def get_teachers_of_courses(cls, courses, **more_user_filters):
        return User.objects.filter(
            enrollments__person=F("id"),
            enrollments__role=cls.EnrollmentRole.teacher,
            enrollments__course__in=courses,
            enrollments__finished_on__isnull=True,
            **more_user_filters
        )

    @classmethod
    def get_users_of_courses(cls, courses):
        return User.objects.filter(
            enrollments__person=F("id"),
            enrollments__course__in=courses,
            enrollments__finished_on__isnull=True
        )
