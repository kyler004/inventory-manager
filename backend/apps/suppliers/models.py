from django.db import models
from django.core.validators import MinValueValidator

class Supplier(models.Model): 
    """
    Companies we buystock from
    From the planning made - Module 4: Supplier & purchase Orders.
    """

    name = models.CharField(max_length=255)
    contact_person = models.CharField(max_length=150, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=30, blank=True) #seems like tke length might be too much, I may return here
    address = models.TextField(blank=True)
    payment_terms = models.CharField(max_length=100, blank=True)
    lead_time_days = models.PositiveIntegerField(default=7)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta: 
        db_table = 'suppliers'
    
    def __str__(self):
        return self.name

class SupplierProduct(models.Model): 
    """
    The link between a supplier and a product.
    Answers: "Who sells this product, at what price,
    and what's their minimum order?"
    """

    supplier = models.ForeignKey(
        Supplier, 
        on_delete=models.CASCADE, 
        related_name='supplier_products'
    )
    product = models.ForeignKey(
        'products.Product', 
        on_delete=models.CASCADE, 
        related_name='supplier_products'
    )
    supplier_sku = models.CharField(max_length=100, blank=True) #Supplier's own code
    unit_cost = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        validators=[MinValueValidator(0)]
    )
    minimum_order_quantity = models.PositiveIntegerField(default=1)
    is_preffered_supplier = models.BooleanField(default=True) # When auto-reorder triggers, it picks the preferred supplier

    class Meta: 
        db_table = 'supplier_products'
        unique_together = ['supplier', 'product'] #No two products with the same name from the same supplier
    
    def __str__(self): 
        return f"{self.supplier.name} => {self.product.name}"