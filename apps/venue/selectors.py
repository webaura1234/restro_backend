from django.core.exceptions import ImproperlyConfigured

from .models import RestaurantConfig


def get_restaurant_config() -> RestaurantConfig:
    """
    Return the single restaurant profile for this database.

    This project assumes **one restaurant per database** with **exactly one**
    ``RestaurantConfig`` row. Use this in views/services instead of ``.first()``
    so misconfiguration fails loudly at runtime.
    """
    rows = list(RestaurantConfig.objects.all()[:2])
    if not rows:
        raise ImproperlyConfigured(
            "RestaurantConfig: no row found. Create exactly one row (admin or migration)."
        )
    if len(rows) > 1:
        raise ImproperlyConfigured(
            "RestaurantConfig: expected exactly one row for single-restaurant-per-database; "
            f"found multiple. Remove extras or split deployments."
        )
    return rows[0]
