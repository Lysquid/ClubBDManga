from django.contrib import admin
from django.contrib.admin.models import LogEntry

admin.site.site_title = "Club BD Manga"
admin.site.site_header = "Club BD Manga"


@admin.register(LogEntry)
class LogEntryAdmin(admin.ModelAdmin):
    search_fields = [
        'object_repr',
        'change_message'
    ]

    list_display = [
        'action_time',
        'user',
        'content_type',
        'action_flag',
        'object_repr'
    ]

    list_filter = [
        'action_flag',
        'user',
        'content_type'
    ]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser
