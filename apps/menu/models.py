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
    is_spicy = models.BooleanField(default=False)
    is_bestseller = models.BooleanField(default=False)
    is_new = models.BooleanField(default=False)
    sort_order = models.PositiveIntegerField(default=0)
    availability = models.CharField(
        max_length=30,
        choices=Availability.choices,
        default=Availability.AVAILABLE,
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["sort_order"]
        indexes = [
            models.Index(fields=["availability", "is_active"]),
        ]

    def __str__(self):
        return self.name


class AddOnGroup(models.Model):
    """
    A group of choices attached to a MenuItem.
    e.g. "Crust Type", "Extra Toppings", "Spice Level"
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    menu_item = models.ForeignKey(
        MenuItem,
        on_delete=models.CASCADE,
        related_name="addon_groups",
    )
    name = models.CharField(max_length=100)
    is_required = models.BooleanField(default=False)
    min_selections = models.PositiveIntegerField(default=0)
    max_selections = models.PositiveIntegerField(default=1)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["sort_order"]

    def __str__(self):
        return f"{self.menu_item.name} — {self.name}"


class AddOnOption(models.Model):
    """
    A single selectable option inside an AddOnGroup.
    e.g. "Extra Cheese +₹50", "Thin Crust +₹0"
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    group = models.ForeignKey(
        AddOnGroup,
        on_delete=models.CASCADE,
        related_name="options",
    )
    name = models.CharField(max_length=100)
    additional_price = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=0.00,
    )
    is_available = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["sort_order"]

    def __str__(self):
        return f"{self.name} (+₹{self.additional_price})"


class MenuItemImage(models.Model):
    """
    Multiple images per MenuItem.
    One image should have is_primary=True — used on menu cards.
    Others shown in item detail modal gallery.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    menu_item = models.ForeignKey(
        MenuItem,
        on_delete=models.CASCADE,
        related_name="images",
    )
    image_url = models.URLField()
    is_primary = models.BooleanField(default=False)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["sort_order"]

    def __str__(self):
        return f"{self.menu_item.name} — image {self.sort_order}"
