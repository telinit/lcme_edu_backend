from django.contrib import admin
from reversion.admin import VersionAdmin

from .models import *


@admin.register(Olympiad)
class OlympiadAdmin(VersionAdmin):
    autocomplete_fields = ['department', 'logo']
    list_display = ['name', 'category', 'organization', 'department']
    list_filter = ('name', 'category', 'organization', 'department')
    search_fields = [
        'name',
        'category',
        'organization',
        'department',
        'website'
    ]
    list_per_page = 500


@admin.register(OlympiadParticipation)
class OlympiadParticipationAdmin (VersionAdmin):
    autocomplete_fields = ['olympiad', 'person']
    list_display = ['olympiad', 'person', 'award']
    list_filter = ('olympiad', 'person', 'award')
    search_fields = [
        'olympiad',
        'person',
        'award'
    ]
    list_per_page = 500
