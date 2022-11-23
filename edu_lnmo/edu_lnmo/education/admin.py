from django.contrib import admin
from reversion.admin import VersionAdmin

from .models import *


@admin.register(EducationSpecialization)
class EducationSpecializationAdmin(VersionAdmin):
    autocomplete_fields = ['department']
    list_display = ['name', 'department']
    list_filter = ('name', 'department')
    search_fields = [
        'name',
        'department__name'
    ]
    list_per_page = 500


@admin.register(Education)
class EducationAdmin(VersionAdmin):
    autocomplete_fields = ['student', 'specialization']
    list_display = ['student', 'started', 'starting_class', 'finished', 'finishing_class']
    list_filter = ('student', 'started', 'starting_class', 'finished', 'finishing_class')
    search_fields = [
        'student__first_name',
        'student__last_name',
        'student__middle_name',
        'student__username'
    ]
    list_per_page = 500
