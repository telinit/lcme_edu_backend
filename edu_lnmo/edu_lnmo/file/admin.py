from django.contrib import admin
from reversion.admin import VersionAdmin

from .models import *


@admin.register(File)
class FileAdmin(VersionAdmin):
    pass
