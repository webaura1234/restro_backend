import uuid

from django.db import models


class RestaurantConfig(models.Model):
    """
    **Singleton (exactly one row per database).** Enforced in admin and
    ``venue.selectors.get_restaurant_config``.

    Operational / legal contact only — branding assets live in the frontend.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    legal_name = models.CharField(max_length=300, blank=True)
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    address = models.TextField()
    timezone = models.CharField(
        max_length=64,
        default="Asia/Kolkata",
        help_text="IANA timezone for receipts and reporting.",
    )
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=18.00)
    currency = models.CharField(max_length=3, default="INR")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "restaurant config"
        verbose_name_plural = "restaurant config"

    def __str__(self):
        return self.name


class Table(models.Model):
    class Status(models.TextChoices):
        EMPTY = "empty", "Empty"
        OCCUPIED = "occupied", "Occupied"
        BILL_REQUESTED = "bill_requested", "Bill Requested"
        CLEANING = "cleaning", "Cleaning"
        RESERVED = "reserved", "Reserved"

    class Section(models.TextChoices):
        INDOOR = "indoor", "Indoor"
        OUTDOOR = "outdoor", "Outdoor"
        VIP = "vip", "VIP"
        BAR = "bar", "Bar"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    table_number = models.CharField(max_length=10, unique=True)
    seating_capacity = models.PositiveIntegerField()
    section = models.CharField(
        max_length=20,
        choices=Section.choices,
        default=Section.INDOOR,
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.EMPTY,
    )
    qr_token = models.CharField(max_length=64, unique=True)
    qr_token_expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["table_number"]

    def __str__(self):
        return f"Table {self.table_number}"
