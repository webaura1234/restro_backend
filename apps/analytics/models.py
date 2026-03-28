import uuid

from django.db import models


class DailyAnalytics(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    date = models.DateField(unique=True)
    total_revenue = models.DecimalField(max_digits=12, decimal_places=2)
    total_orders = models.IntegerField()
    dine_in_revenue = models.DecimalField(max_digits=12, decimal_places=2)
    swiggy_revenue = models.DecimalField(max_digits=12, decimal_places=2)
    zomato_revenue = models.DecimalField(max_digits=12, decimal_places=2)
    avg_order_value = models.DecimalField(max_digits=8, decimal_places=2)
    avg_table_duration_mins = models.IntegerField()
    payment_method_breakdown = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date"]
        verbose_name_plural = "daily analytics"

    def __str__(self):
        return str(self.date)


class ItemAnalytics(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    menu_item = models.ForeignKey(
        "menu.MenuItem",
        on_delete=models.PROTECT,
        related_name="analytics_rows",
    )
    date = models.DateField()
    quantity_sold = models.IntegerField(default=0)
    revenue = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date", "menu_item_id"]
        constraints = [
            models.UniqueConstraint(
                fields=["menu_item", "date"],
                name="analytics_itemanalytics_menu_item_date_uniq",
            ),
        ]

    def __str__(self):
        return f"{self.menu_item_id} @ {self.date}"
