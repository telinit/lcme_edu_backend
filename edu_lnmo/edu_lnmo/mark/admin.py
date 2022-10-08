from django.contrib import admin
from reversion.admin import VersionAdmin

from .models import *


@admin.register(Mark)
class MarkAdmin(VersionAdmin):
    pass
