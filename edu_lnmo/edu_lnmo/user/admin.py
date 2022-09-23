from django.contrib import admin
from reversion.admin import VersionAdmin

from .models import *


@admin.register(User)
class UserAdmin(VersionAdmin):
    pass
