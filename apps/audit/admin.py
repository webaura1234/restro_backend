from django.contrib import admin

from .models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ("timestamp", "action", "entity_type", "entity_id", "user", "ip_address")
    list_filter = ("entity_type", "action")
    search_fields = ("entity_id", "action", "ip_address")
    readonly_fields = (
        "id",
        "user",
        "action",
        "entity_type",
        "entity_id",
        "old_value",
        "new_value",
        "ip_address",
        "timestamp",
    )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
