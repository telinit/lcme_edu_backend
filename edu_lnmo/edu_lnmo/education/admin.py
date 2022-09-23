from django.contrib import admin
from reversion.admin import VersionAdmin

from .models import *


@admin.register(EducationSpecialization)
class EducationSpecializationAdmin(VersionAdmin):
    pass


@admin.register(Education)
class EducationAdmin(VersionAdmin):
    pass
