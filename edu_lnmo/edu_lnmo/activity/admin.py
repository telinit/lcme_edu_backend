from django.contrib import admin
from reversion.admin import VersionAdmin

from .models import *


@admin.register(Activity)
class ActivityAdmin(VersionAdmin):
    autocomplete_fields = ['course', 'files', 'linked_activity']
    list_display = ['content_type', 'order', 'title', 'course']
    list_filter = ('content_type', 'course')
    search_fields = [
        'title',
        'course'
    ]
    list_per_page = 500