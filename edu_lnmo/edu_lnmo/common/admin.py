from django.contrib import admin
from reversion.admin import VersionAdmin

from .models import *


@admin.register(Organization)
class OrganizationAdmin(VersionAdmin):
    autocomplete_fields = []
    list_display = ['name', 'name_short']
    list_filter = ('name', 'name_short')
    search_fields = [
        'name',
        'name_short'
    ]


@admin.register(Department)
class DepartmentAdmin(VersionAdmin):
    autocomplete_fields = ['organization']
    list_display = ['name', 'organization']
    list_filter = ('name', 'organization')
    search_fields = [
        'name',
        'organization'
    ]
