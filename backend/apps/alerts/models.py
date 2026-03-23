from django.db import models


class Alert(models.Model):
    """
    Persistent notification log.
    Created by Celery tasks, pushed via WebSocket to the frontend.
    From our planning — Module 8: Reporting & Alerts.
    """

    class AlertType(models.TextChoices):
        LOW_STOCK = 'low_stock', 'Low Stock'
        OUT_OF_STOCK = 'out_of_stock', 'Out of Stock'
        NEAR_EXPIRY = 'near_expiry', 'Near Expiry'
        EXPIRED = 'expired', 'Expired'
        PO_OVERDUE = 'po_overdue', 'Purchase Order Overdue'
        TRANSFER_PENDING = 'transfer_pending', 'Transfer Pending'

    location = models.ForeignKey(
        'locations.Location',
        on_delete=models.CASCADE,
        related_name='alerts'
    )
    type = models.CharField(max_length=30, choices=AlertType.choices)
    message = models.TextField()

    # Generic reference to any related object (product, PO, batch...)
    entity_type = models.CharField(max_length=50, blank=True)   # e.g. "product"
    entity_id = models.PositiveIntegerField(null=True, blank=True)  # e.g. 42

    is_resolved = models.BooleanField(default=False)
    resolved_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='resolved_alerts'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'alerts'
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.type}] {self.message[:50]}"