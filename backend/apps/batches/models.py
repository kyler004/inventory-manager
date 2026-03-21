from django.db import models
from django.utils import timezone

class Batch(models.Model):
    """
    Tracks a specific lot of a product within an expiry date.
    Critical for perishables - enforces FIFO
    From our planning _ Module 5: Batch and Expiry Tracking.
    """

    class BatchStatus(models.TextChoices):
        ACTIVE = 'active', 'Active'
        NEAR_EXPIRY = 'near_expiry', 'Near Expiry'
        EXPIRED = 'expired', 'Expired'
        DISPOSED = 'disposed', 'Disposed'

    product = models.ForeignKey(
        'products.Product', 
        on_delete=models.PROTECT, 
        related_name='batches'
    )
    location = models.ForeignKey(
        'locations.Location', 
        on_delete=models.PROTECT, 
        related_name='batches'
    )
    batch_number = models.CharField(max_length=100)
    manufacture_date = models.DateField(null=True, blank=True)
    expiry_date = models.DateField(null=True, blank=True)
    quantity_remaining = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0
    )
    status = models.CharField(
        max_length=20, 
        choices=BatchStatus.choices, 
        default=BatchStatus.ACTIVE
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta: 
        db_table = 'batches'
        ordering = ['expiry_date'], 
        verbose_name_plural = 'batches'
    
    @property
    def days_until_expiry(self): 
        if self.expiry_date: 
            delta = self.expiry_date - timezone.now().date()
            return delta.days
        return None

    @property
    def is_expired(self): 
        if self.expiry_date: 
            return timezone.now().date() > self.expiry_date
        return False

    def __str__(self):
        return f"{self.product.name} — Batch {self.batch_number} (exp: {self.expiry_date})"