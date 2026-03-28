import uuid

from django.db import models


class Category(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    sort_order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["sort_order", "name"]
        verbose_name_plural = "categories"

    def __str__(self):
        return self.name


class MenuItem(models.Model):
    class Availability(models.TextChoices):
        AVAILABLE = "available", "Available"
        OUT_OF_STOCK = "out_of_stock", "Out of stock"
        UNAVAILABLE_FOR_DELIVERY = (
            "unavailable_for_delivery",
            "Unavailable for delivery",
        )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="items",
    )
    name = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    cost_price = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
    )
    image_url = models.URLField(null=True, blank=True)
    prep_time_mins = models.IntegerField(default=15)
    is_vegetarian = models.BooleanField(default=False)
    is_vegan = models.BooleanField(default=False)
    availability = models.CharField(
        max_length=30,
        choices=Availability.choices,
        default=Availability.AVAILABLE,
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["availability", "is_active"]),
        ]

    def __str__(self):
        return self.name
