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
    list_display = ['person', 'course', 'role', 'finished_on']
    list_filter = ('person', 'course', 'role', 'finished_on')
    search_fields = [
        'person__first_name',
        'person__last_name',
        'person__middle_name',
        'person__username',
        'course__title'
    ]

