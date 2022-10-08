from django.db.models import *

from ..common.models import CommonObject
from ..file.models import File
from ..user.models import User


class Course(CommonObject):
    title       = CharField(max_length=255, verbose_name="Название", blank=False)
    description = TextField(verbose_name="Описание")

    logo        = ForeignKey(File, related_name="logo", verbose_name="Логотип", blank=True, null=True, on_delete=SET_NULL)
    cover       = ForeignKey(File, related_name="cover", verbose_name="Обложка", blank=True, null=True, on_delete=SET_NULL)

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
        teacher  = 't', "Преподаватель"
        student  = 's', "Учащийся"

    person      = ForeignKey(User, verbose_name="Пользователь", related_name="enrollments", on_delete=CASCADE)
    course      = ForeignKey(Course, verbose_name="Курс", related_name="enrollments", on_delete=CASCADE)
    group       = CharField(verbose_name="Группа", max_length=255, null=True, blank=True)
    role        = CharField(choices=EnrollmentRole.choices, max_length=3)
    finished_on = DateTimeField(verbose_name="Завершена", null=True)

    @classmethod
    def get_courses_of_teacher(self, user):
        q1 = Course.objects.filter(
            enrollments__role=self.EnrollmentRole.teacher,
            enrollments__finished_on__isnull=True,
            enrollments__person=user
        )
        # q2 = CourseEnrollment.objects.filter(
        #     person=user,
        #     role=self.EnrollmentRole.teacher,
        #     finished_on__isnull=True
        # ).values("course")

        return q1

    @classmethod
    def get_courses_of_student(self, user):
        return CourseEnrollment.objects.filter(
            person=user,
            role=self.EnrollmentRole.student,
            finished_on__isnull=True
        ).values("course")

    @classmethod
    def get_students_of_courses(self, courses):
        return CourseEnrollment.objects.filter(
            course__in=courses,
            role=self.EnrollmentRole.student,
            finished_on__isnull=True
        ).values("person")


    @classmethod
    def get_teachers_of_courses(self, courses):
        return CourseEnrollment.objects.filter(
            course__in=courses,
            role=self.EnrollmentRole.teacher,
            finished_on__isnull=True
        ).values("person")
