import uuid

from django.conf import settings
from django.db import models


class TableSession(models.Model):
    class Status(models.TextChoices):
        OPEN = "open", "Open"
        BILL_REQUESTED = "bill_requested", "Bill requested"
        PAID = "paid", "Paid"
        CLOSED = "closed", "Closed"
        ABANDONED = "abandoned", "Abandoned"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    table = models.ForeignKey(
        "venue.Table",
        on_delete=models.PROTECT,
        related_name="sessions",
    )
    qr_token_used = models.CharField(max_length=64)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.OPEN,
    )
    opened_at = models.DateTimeField(auto_now_add=True)
    bill_requested_at = models.DateTimeField(null=True, blank=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    closed_at = models.DateTimeField(null=True, blank=True)
    captain = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="table_sessions_attended",
    )
    notes = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ["-opened_at"]

    def __str__(self):
        return f"Session {self.id} @ {self.table_id}"
