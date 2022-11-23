from django.contrib import admin
from reversion.admin import VersionAdmin

from .models import *


@admin.register(Olympiad)
class OlympiadAdmin(VersionAdmin):
    autocomplete_fields = ['department']
    list_display = ['name', 'category', 'location', 'department']
    list_filter = ('name', 'category', 'location', 'department')
    search_fields = [
        'name',
        'category',
        'location',
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
