from django.contrib import admin

from .models import Category, MenuItem


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "sort_order", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name",)


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "category",
        "price",
        "cost_price",
        "prep_time_mins",
        "availability",
        "is_active",
    )
    list_filter = ("availability", "is_active", "is_vegetarian", "is_vegan")
    search_fields = ("name", "description")
    autocomplete_fields = ("category",)
