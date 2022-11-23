from django.contrib import admin
from reversion.admin import VersionAdmin

from .models import UnreadObject


@admin.register(UnreadObject)
class UnreadObjectAdmin(VersionAdmin):
    autocomplete_fields = ['user']
    list_display = ['type', 'user', 'created']
    list_filter = ('type', 'user')
    search_fields = [
        'obj',
        'type',
        'user'
    ]
    list_per_page = 500