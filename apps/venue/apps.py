from django.apps import AppConfig


class VenueConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.venue"
    label = "venue"
    verbose_name = "Venue & restaurant settings"
