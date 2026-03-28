from django.contrib import admin

from .models import Bill, Payment


class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 0
    autocomplete_fields = ("collected_by",)


@admin.register(Bill)
class BillAdmin(admin.ModelAdmin):
    list_display = ("id", "session", "status", "total_amount", "amount_paid", "created_at")
    list_filter = ("status",)
    search_fields = ("id", "session__table__table_number")
    inlines = [PaymentInline]
    autocomplete_fields = ("session", "locked_by")


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "bill",
        "amount",
        "commission_pct",
        "commission_amount",
        "net_settlement",
        "method",
        "gateway",
        "status",
        "created_at",
    )
    list_filter = ("method", "gateway", "status")
    search_fields = ("razorpay_order_id", "razorpay_payment_id")
    autocomplete_fields = ("bill", "collected_by")
