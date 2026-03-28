from django.contrib import admin

from .models import TableSession


@admin.register(TableSession)
class TableSessionAdmin(admin.ModelAdmin):
    list_display = ("id", "table", "status", "opened_at", "captain", "notes")
    list_filter = ("status",)
    autocomplete_fields = ("table", "captain")
    search_fields = ("id", "qr_token_used", "notes")
