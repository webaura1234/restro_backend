from django.contrib import admin

from .models import AddOnGroup, AddOnOption, Category, MenuItem, MenuItemImage


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "sort_order", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name",)


class MenuItemImageInline(admin.TabularInline):
    model = MenuItemImage
    extra = 0


class AddOnGroupInline(admin.StackedInline):
    model = AddOnGroup
    extra = 0
    show_change_link = True


class AddOnOptionInline(admin.TabularInline):
    model = AddOnOption
    extra = 0


@admin.register(AddOnGroup)
class AddOnGroupAdmin(admin.ModelAdmin):
    list_display = ("name", "menu_item", "is_required", "min_selections", "max_selections", "sort_order")
    list_filter = ("is_required",)
    search_fields = ("name", "menu_item__name")
    autocomplete_fields = ("menu_item",)
    inlines = [AddOnOptionInline]


@admin.register(AddOnOption)
class AddOnOptionAdmin(admin.ModelAdmin):
    list_display = ("name", "group", "additional_price", "is_available", "sort_order")
    list_filter = ("is_available",)
    search_fields = ("name", "group__name", "group__menu_item__name")
    autocomplete_fields = ("group",)


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "category",
        "price",
        "cost_price",
        "prep_time_mins",
        "sort_order",
        "is_bestseller",
        "is_new",
        "is_spicy",
        "availability",
        "is_active",
    )
    list_filter = (
        "availability",
        "is_active",
        "is_vegetarian",
        "is_vegan",
        "is_spicy",
        "is_bestseller",
        "is_new",
    )
    search_fields = ("name", "description")
    autocomplete_fields = ("category",)
    inlines = [MenuItemImageInline, AddOnGroupInline]
