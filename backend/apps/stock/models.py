from django.db import models
from django.core.validators import MinValueValidator

class StockLevel(models.Model): 
    """
    The CURRENT Sstock for one product at one location.
    This is what the dashboard will display in real time.
    One Row per product per location
    """
    product = models.ForeignKey(
        'products.Product', 
        on_delete=models.PROTECT, 
        related_name='stock_levels'
    )
    location = models.ForeignKey(
        'locations.Location', 
        on_delete=models.PROTECT, 
        related_name='stock_levels'
    )
    zone = models.ForeignKey(
        'locations.Zone', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='stock_levels'
    )
    quantity_on_hand = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0, 
        validators=[MinValueValidator(0)]
    )
    quantity_reserved = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0, 
        validators=[MinValueValidator(0)]
    )
    reorder_point = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0
    )
    reorder_quantity = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True, 
    )
    last_updated = models.DateTimeField(auto_now=True)

    class Meta: 
        db_table = 'stock_levels'
        unique_together = ['product', 'location'] #one row per product per location
    
    @property
    def quantity_available(self): 
        """what is actually available"""
        return self.quantity_on_hand - self.quantity_reserved

    @property
    def stock_status(self): 
        """
        Used by the front end to show OK / LOW/ OUT badges
        Connects to StockLevelBadge.tsx from our front end plan.
        """

        if self.quantity_available <= 0: 
            return 'OUT'
        if self.quantity_available <= self.reorder_point: 
            return 'LOW'
        return 'OK'
    
    def __str__(self):
        return f"{self.product.name} @ {self.location.name}: {self.quantity_on_hand}"
    
class StockMovement(models.Model): 
    """
    An IMMUTABLE log of every single stock change.
    Never updated or deleted — only appended to.
    This is our audit trail for shrinkage detection.
    From our planning — Module 3: Stock Management.
    """

    class MovementType(models.Model): 
        RECEIVING = 'receiving', 'Receiving'        # Goods arrived from supplier
        SALE = 'sale', 'Sale'                       # Sold at POS
        TRANSFER_IN = 'transfer_in', 'Transfer In'  # Arrived from another location
        TRANSFER_OUT = 'transfer_out', 'Transfer Out'
        ADJUSTMENT = 'adjustment', 'Adjustment'     # Manual correction
        RETURN = 'return', 'Return'                 # Customer return
        DISPOSAL = 'disposal', 'Disposal'           # Expired/damaged write-off

    product = models.ForeignKey(
        'products.Product', 
        on_delete=models.PROTECT, 
        related_name='movements'
    )
    from_location = models.ForeignKey(
        'location.Location', 
        on_delete=models.PROTECT, 
        null=True, 
        blank=True, 
        related_name='outgoing_movements'
    )
    to_location = models.ForeignKey(
        'locations.Location', 
        on_delete=models.PROTECT, 
        null=True, 
        blank=True, 
        related_name='incoming_movements'
    )
    batch = models.ForeignKey(
        'batches.Batch', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='movements'
    )
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    movement_type = models.CharField(max_length=20, choices=MovementType.choices)
    reference_id = models.CharField(max_length=100, blank=True)  # PO number, Transfer ID etc.
    performed_by = models.ForeignKey(
        'users.User', 
        on_delete=models.PROTECT, 
        related_name='stock_movements'
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    # No updated_at field as this is an immutable report

    class Meta: 
        db_table = 'stock_movements'
        ordering = ['-created_at'] #Most Recent first
    
    def __str__(self): 
        return f"{self.movement_type} - {self.product.name} x{self.quantity}"

