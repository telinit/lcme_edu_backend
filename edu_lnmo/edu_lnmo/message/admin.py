from django.contrib import admin
from reversion.admin import VersionAdmin

from .models import *


@admin.register(Message)
class MessageAdmin(VersionAdmin):
    autocomplete_fields = ['thread', 'sender', 'receiver', 'attachments']
    list_display = ['type', 'sender', 'receiver']
    list_filter = ('type', 'sender', 'receiver')
    search_fields = [
        'type',
        'sender',
        'receiver',
        'body'
    ]


@admin.register(MessageThread)
class MessageThreadAdmin(VersionAdmin):
    autocomplete_fields = ['members', 'group']
    list_display = ['type', 'topic', 'support_status']
    list_filter = ('type', 'topic', 'support_status')
    search_fields = [
        'type',
        'topic',
        'members',
        'support_status',
        'group'
    ]

@admin.register(ThreadGroup)
class ThreadGroupAdmin(VersionAdmin):
    autocomplete_fields = ['parent']
    list_display = ['name', 'parent']
    list_filter = ('name', 'parent')
    search_fields = [
        'name',
        'parent'
    ]