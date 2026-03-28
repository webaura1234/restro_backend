from django.contrib import admin

from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    ordering = ("email",)
    list_display = ("email", "name", "role", "is_staff", "is_active")
    list_filter = ("role", "is_staff", "is_active")
    search_fields = ("email", "name", "phone")
    readonly_fields = ("created_at",)

    fieldsets = (
        (None, {"fields": ("email",)}),
        ("Profile", {"fields": ("phone", "name", "locale", "role")}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Meta", {"fields": ("created_at",)}),
    )

    filter_horizontal = ("groups", "user_permissions")
