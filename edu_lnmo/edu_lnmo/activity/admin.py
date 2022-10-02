from django.contrib import admin
from reversion.admin import VersionAdmin

from .models import *


@admin.register(Activity)
class ActivityAdmin(VersionAdmin):
    pass