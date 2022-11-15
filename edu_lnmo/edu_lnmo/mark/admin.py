from django.contrib import admin
from reversion.admin import VersionAdmin

from .models import *


@admin.register(Mark)
class MarkAdmin(VersionAdmin):
    autocomplete_fields = ['author', 'student']
    list_display = ['activity', 'student', 'value', 'author']
    list_filter = ('activity', 'student', 'value', 'author')
    search_fields = [
        'author',
        'student',
        'value',
        'comment',
        'activity'
    ]
