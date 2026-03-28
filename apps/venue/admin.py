from django.contrib import admin

from .models import RestaurantConfig, Table


@admin.register(RestaurantConfig)
class RestaurantConfigAdmin(admin.ModelAdmin):
    list_display = ("name", "currency", "timezone", "updated_at")
    fieldsets = (
        (None, {"fields": ("name", "legal_name", "phone", "email", "address")}),
        ("Operations", {"fields": ("timezone", "tax_rate", "currency")}),
        ("Meta", {"fields": ("updated_at",)}),
    )
    readonly_fields = ("updated_at",)

    def has_add_permission(self, request):
        return not RestaurantConfig.objects.exists()


@admin.register(Table)
class TableAdmin(admin.ModelAdmin):
    list_display = ("table_number", "section", "seating_capacity", "status")
    list_filter = ("status", "section")
    search_fields = ("table_number", "section")
