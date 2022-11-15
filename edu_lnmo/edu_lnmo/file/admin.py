from django.contrib import admin
from reversion.admin import VersionAdmin

from .models import *


@admin.register(File)
class FileAdmin(VersionAdmin):
    autocomplete_fields = []
    list_display = ['name', 'size', 'mime_type', 'hash']
    list_filter = ('name', 'mime_type')
    search_fields = [
        'name'
    ]
