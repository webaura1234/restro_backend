from django.contrib import admin

from .models import DailyAnalytics, ItemAnalytics


@admin.register(DailyAnalytics)
class DailyAnalyticsAdmin(admin.ModelAdmin):
    list_display = ("date", "total_revenue", "total_orders", "avg_order_value")
    ordering = ("-date",)


@admin.register(ItemAnalytics)
class ItemAnalyticsAdmin(admin.ModelAdmin):
    list_display = ("date", "menu_item", "quantity_sold", "revenue")
    list_filter = ("date",)
    autocomplete_fields = ("menu_item",)
