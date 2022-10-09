from django.db.models import *
from rest_framework.viewsets import ViewSet

from ..common.models import CommonObject
from ..education.models import EducationSpecialization
from ..file.models import File
from ..user.models import User


class Course(CommonObject):
    title = CharField(max_length=255, verbose_name="Название", blank=False)
    description = TextField(verbose_name="Описание")

    for_class = CharField(max_length=10, verbose_name="Класс", blank=True)
    for_specialization = ForeignKey(
        EducationSpecialization,
        verbose_name="Направление обучения",
        related_name="courses",
        on_delete=SET_NULL,
        blank=True,
        null=True
    )

    logo = ForeignKey(File, related_name="logo", verbose_name="Логотип", blank=True, null=True, on_delete=SET_NULL)
    cover = ForeignKey(File, related_name="cover", verbose_name="Обложка", blank=True, null=True, on_delete=SET_NULL)

    def __str__(self):
        return f"{self.title}"

    @property
    def teachers(self):
        return CourseEnrollment.objects.filter(
            course=self,
            finished_on=None,
            role=CourseEnrollment.EnrollmentRole.teacher
        )

    @property
    def students(self):
        return CourseEnrollment.objects.filter(
            course=self,
            finished_on=None,
            role=CourseEnrollment.EnrollmentRole.student
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

    person = ForeignKey(User, verbose_name="Пользователь", related_name="enrollments", on_delete=CASCADE)
    course = ForeignKey(Course, verbose_name="Курс", related_name="enrollments", on_delete=CASCADE)
    group = CharField(verbose_name="Группа", max_length=255, null=True, blank=True)
    role = CharField(choices=EnrollmentRole.choices, max_length=3)
    finished_on = DateTimeField(verbose_name="Завершена", null=True)

    @classmethod
    def get_courses_of_teacher(cls, user) -> QuerySet:
        return Course.objects.filter(
            enrollments__role=cls.EnrollmentRole.teacher,
            enrollments__finished_on__isnull=True,
            enrollments__person=user
        )

    @classmethod
    def get_courses_of_student(cls, user):
        return Course.objects.filter(
            enrollments__role=cls.EnrollmentRole.student,
            enrollments__finished_on__isnull=True,
            enrollments__person=user
        )

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
    def get_students_of_courses(cls, courses):
        return User.objects.filter(
            enrollments__person=F("id"),
            enrollments__role=cls.EnrollmentRole.student,
            enrollments__course__in=courses,
            enrollments__finished_on__isnull=True
        )

    @classmethod
    def get_teachers_of_courses(cls, courses):
        return User.objects.filter(
            enrollments__person=F("id"),
            enrollments__role=cls.EnrollmentRole.teacher,
            enrollments__course__in=courses,
            enrollments__finished_on__isnull=True
        )

    @classmethod
    def get_users_of_courses(cls, courses):
        return User.objects.filter(
            enrollments__person=F("id"),
            enrollments__course__in=courses,
            enrollments__finished_on__isnull=True
        )
