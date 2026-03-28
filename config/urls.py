from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/accounts/", include("apps.accounts.urls")),
    path("api/v1/venue/", include("apps.venue.urls")),
    path("api/v1/menu/", include("apps.menu.urls")),
    path("api/v1/sessions/", include("apps.sessions.urls")),
    path("api/v1/orders/", include("apps.orders.urls")),
    path("api/v1/billing/", include("apps.billing.urls")),
    path("api/v1/analytics/", include("apps.analytics.urls")),
    path("api/v1/audit/", include("apps.audit.urls")),
]
