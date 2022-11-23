from django.contrib import admin
from reversion.admin import VersionAdmin

from .models import *


@admin.register(Course)
class CourseAdmin(VersionAdmin):
    autocomplete_fields = ['for_specialization', 'logo', 'cover']
    list_display = ['title', 'type', 'for_class', 'for_specialization', 'for_group']
    list_filter = ('type', 'for_class', 'for_specialization', 'for_group')
    search_fields = [
        'for_specialization__name',
        'title'
    ]


@admin.register(CourseEnrollment)
class CourseEnrollmentAdmin(VersionAdmin):
    autocomplete_fields = ['person', 'course']
    list_display = ['get_course_title', 'get_course_class', 'get_course_specialization', 'get_course_group', 'role', 'person', 'finished_on']
    list_filter = ('course__title', 'course__for_class', 'course__for_specialization__name', 'course__for_group', 'role', 'finished_on')
    search_fields = [
        'person__first_name',
        'person__last_name',
        'person__middle_name',
        'person__username',
        'course__title'
    ]

    @admin.display(description='Курс', ordering='course__title')
    def get_course_title(self, enr: CourseEnrollment):
        return enr.course.title

    @admin.display(description='Класс', ordering='course__for_class')
    def get_course_class(self, enr: CourseEnrollment):
        return enr.course.for_class

    @admin.display(description='Направление', ordering='course__for_specialization')
    def get_course_specialization(self, enr: CourseEnrollment):
        return enr.course.for_specialization

    @admin.display(description='Группа', ordering='course__for_group')
    def get_course_group(self, enr: CourseEnrollment):
        return enr.course.for_group
