from django.contrib import admin
from reversion.admin import VersionAdmin

from .models import *


@admin.register(Organization)
class OrganizationAdmin(VersionAdmin):
    pass


@admin.register(Department)
class DepartmentAdmin(VersionAdmin):
    pass
