from django.contrib import admin
from reversion.admin import VersionAdmin

from .models import *


@admin.register(OlympiadParticipation)
class OlympiadParticipationAdmin(VersionAdmin):
    pass


@admin.register(Olympiad)
class OlympiadAdmin(VersionAdmin):
    pass