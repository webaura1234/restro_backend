from django.contrib import admin

from .models import Order, OrderItem, OrderItemAddOn


class OrderItemAddOnInline(admin.TabularInline):
    model = OrderItemAddOn
    extra = 0
    autocomplete_fields = ("addon_option",)


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    autocomplete_fields = ("menu_item",)
    show_change_link = True


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "order_number",
        "external_order_id",
        "channel",
        "status",
        "total_amount",
        "created_at",
    )
    list_filter = ("channel", "status")
    search_fields = ("order_number", "external_order_id")
    inlines = [OrderItemInline]
    autocomplete_fields = ("session", "confirmed_by")
    readonly_fields = ("order_number",)


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ("name", "order", "quantity", "subtotal")
    autocomplete_fields = ("order", "menu_item")
    inlines = [OrderItemAddOnInline]
