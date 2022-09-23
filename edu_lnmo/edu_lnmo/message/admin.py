from django.contrib import admin
from reversion.admin import VersionAdmin

from .models import *


@admin.register(Message)
class MessageAdmin(VersionAdmin):
    pass


@admin.register(MessagePrivate)
class MessagePrivateAdmin(VersionAdmin):
    pass


@admin.register(MessageTaskSubmission)
class MessageTaskSubmissionAdmin(VersionAdmin):
    pass


@admin.register(MessageNews)
class MessageNewsAdmin(VersionAdmin):
    pass
