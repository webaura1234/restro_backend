import datetime
import uuid

from django.conf import settings
from django.db import models


class Order(models.Model):
    class Channel(models.TextChoices):
        DINE_IN = "dine_in", "Dine in"
        WEBSITE = "website", "Website / online"
        TAKEAWAY = "takeaway", "Takeaway"
        PHONE = "phone", "Phone order"
        SWIGGY = "swiggy", "Swiggy"
        ZOMATO = "zomato", "Zomato"
        OTHER = "other", "Other"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        CONFIRMED = "confirmed", "Confirmed"
        PREPARING = "preparing", "Preparing"
        READY = "ready", "Ready"
        SERVED = "served", "Served"
        CANCELLED = "cancelled", "Cancelled"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey(
        "table_sessions.TableSession",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="orders",
    )
    external_order_id = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        unique=True,
    )
    order_number = models.CharField(
        max_length=20,
        unique=True,
        blank=True,
    )
    channel = models.CharField(max_length=20, choices=Channel.choices)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    special_request = models.TextField(null=True, blank=True)
    confirmed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="confirmed_orders",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    ready_at = models.DateTimeField(null=True, blank=True)
    served_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["channel", "created_at"]),
            models.Index(fields=["session"]),
        ]
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        if not self.order_number:
            today = datetime.date.today()
            prefix = today.strftime("%Y%m%d")
            last = (
                Order.objects.filter(order_number__startswith=prefix)
                .order_by("order_number")
                .last()
            )
            if last:
                last_seq = int(last.order_number[-4:])
                seq = str(last_seq + 1).zfill(4)
            else:
                seq = "0001"
            self.order_number = f"{prefix}-{seq}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.order_number or str(self.pk)


class OrderItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items",
    )
    menu_item = models.ForeignKey(
        "menu.MenuItem",
        on_delete=models.PROTECT,
        related_name="order_items",
    )
    name = models.CharField(max_length=200)
    unit_price = models.DecimalField(max_digits=8, decimal_places=2)
    quantity = models.IntegerField()
    subtotal = models.DecimalField(max_digits=8, decimal_places=2)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return f"{self.name} x{self.quantity}"


class OrderItemAddOn(models.Model):
    """
    Snapshot of a selected AddOnOption at order time.
    Name and price are copied from AddOnOption at the moment
    the order is placed — never reference AddOnOption live
    after this point. This keeps historical bills accurate
    even if the addon name or price changes later.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order_item = models.ForeignKey(
        OrderItem,
        on_delete=models.CASCADE,
        related_name="addons",
    )
    addon_option = models.ForeignKey(
        "menu.AddOnOption",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    name = models.CharField(max_length=100)
    additional_price = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=0.00,
    )

    def __str__(self):
        return f"{self.name} (+₹{self.additional_price})"
