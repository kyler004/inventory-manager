from django.db import models


class StockTransfer(models.Model):
    """
    Moves stock between two locations.
    e.g. Warehouse → Store Branch, or Store A → Store B.
    From our planning — Module 6: Stock Transfers.
    """

    class Status(models.TextChoices):
        REQUESTED = 'requested', 'Requested'
        APPROVED = 'approved', 'Approved'
        IN_TRANSIT = 'in_transit', 'In Transit'
        COMPLETED = 'completed', 'Completed'
        CANCELLED = 'cancelled', 'Cancelled'

    from_location = models.ForeignKey(
        'locations.Location',
        on_delete=models.PROTECT,
        related_name='outgoing_transfers'
    )
    to_location = models.ForeignKey(
        'locations.Location',
        on_delete=models.PROTECT,
        related_name='incoming_transfers'
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.REQUESTED
    )
    requested_by = models.ForeignKey(
        'users.User',
        on_delete=models.PROTECT,
        related_name='transfers_requested'
    )
    approved_by = models.ForeignKey(
        'users.User',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='transfers_approved'
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'stock_transfers'
        ordering = ['-created_at']

    def __str__(self):
        return f"Transfer {self.id}: {self.from_location} → {self.to_location} ({self.status})"


class StockTransferItem(models.Model):
    """A single product line within a transfer."""
    transfer = models.ForeignKey(
        StockTransfer,
        on_delete=models.CASCADE,
        related_name='items'
    )
    product = models.ForeignKey(
        'products.Product',
        on_delete=models.PROTECT,
        related_name='transfer_items'
    )
    batch = models.ForeignKey(
        'batches.Batch',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='transfer_items'
    )
    quantity_requested = models.DecimalField(max_digits=10, decimal_places=2)
    quantity_sent = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    quantity_received = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    class Meta:
        db_table = 'stock_transfer_items'

    def __str__(self):
        return f"{self.product.name} x{self.quantity_requested}"
