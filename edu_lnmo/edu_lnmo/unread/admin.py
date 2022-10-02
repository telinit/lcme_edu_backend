from django.contrib import admin
from reversion.admin import VersionAdmin

from .models import *


@admin.register(Activity)
class ActivityAdmin(VersionAdmin):
    pass


@admin.register(ActivityArticle)
class ActivityArticleAdmin(VersionAdmin):
    pass


@admin.register(ActivityTask)
class ActivityTaskAdmin(VersionAdmin):
    pass


@admin.register(ActivityLink)
class ActivityLinkAdmin(VersionAdmin):
    pass


@admin.register(ActivityMedia)
class ActivityMediaAdmin(VersionAdmin):
    pass
