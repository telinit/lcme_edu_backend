from django.contrib import admin
from reversion.admin import VersionAdmin

from .models import UnreadObject


@admin.register(UnreadObject)
class UnreadObjectAdmin(VersionAdmin):
    pass