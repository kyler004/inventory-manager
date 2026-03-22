from django.db import models
from django.core.validators import MinValueValidator

class PurchaseOrder(models.Model):
    """
    A formal order placed with a supplier.
    Follows the status from our API design: 
    draft -> sent -> confirmed -> recieved
    """

    class Status(models.TextChoices):
        DRAFT = 'draft', 'Draft'
        SENT = 'sent', 'Sent'
        CONFIRMED = 'confirmed', 'Confirmed'
        PARTIALLY_RECEIVED = 'partially_received', 'Partially Received'
        RECEIVED = 'received', 'Received'
        CANCELLED = 'cancelled', 'Cancelled'
    
    supplier = models.ForeignKey(
        'suppliers.Supplier', 
        on_delete=models.PROTECT, 
        related_name='purchase_orders'
    )
    destination_location = models.ForeignKey(
        'locations.Location', 
        on_delete=models.PROTECT, 
        related_name='purchase_orders'
    )
    status = models.CharField(
        max_length=25, 
        choices=Status.choices, 
        default=Status.DRAFT
    )
    order_date = models.DateField(auto_now_add=True)
    expected_delivery_date = models.DateField(null=True, blank=True)
    total_amount = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        default=0
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta: 
        db_table = 'purchase_orders'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"PO-{self.id:05d} - {self.supplier.name} ({self.status})"

class PurchaseOrderItem(models.Model): 
    """A single line item within a purchase order"""
    purchase_order = models.ForeignKey(
        PurchaseOrder, 
        on_delete=models.CASCADE, 
        related_name = 'items'
    )
    product = models.ForeignKey(
        'products.Product', 
        on_delete=models.PROTECT, 
        related_name='purchase_order_items'
    )
    quantity_ordered = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        validators=[MinValueValidator(1)]
    )
    quantity_received = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0
    )
    unit_cost = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        validators=[MinValueValidator(0)]
    )

    class Meta: 
        db_table = 'purchase_order_items'
    
    @property
    def subtotal(self):
        return self.quantity_ordered * self.unit_cost
    
    @property
    def is_fully_received(self): 
        return self.quantity_received >= self.quantity_ordered
    
    def __str__(self):
        return f"{self.product.name} x{self.quantity_ordered}"