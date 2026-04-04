from django.db import models
from django.core.validators import MinValueValidator

class Category(models.Model):
    """
    Self-referencing model - a category can have a parent category.
    e.g "Beverages" => "Dairy Drinks" => "Milk"
    This creates a tree structure for our product catalog.
    """
    name = models.CharField(max_length=100)
    parent = models.ForeignKey(
        'self', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='subcategories'
    )

    class Meta: 
        db_table = 'categories'
        verbose_name_plural = 'categories'
    
    def __str__(self): 
        if self.parent: 
            return f"{self.parent.name} => {self.name}"
        return self.name

class Product(models.Model):
    """
    The foundation of the entire system.
    From our planning - Module 1: Product catalog
    Every other module will reference the product
    """

    class UnitofMeasure(models.TextChoices): 
        KG = 'kg', 'Kilogram'
        LITRE = 'litre', 'Litre'
        PIECE = 'piece', 'Piece'
        PACK = 'pack', 'Pack'
        BOX = 'box', 'Box'
        GRAM = 'gram', 'Gram'
        ML = 'ml', 'Millilitre'

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    sku = models.CharField(max_length=100, unique=True) #internal code
    barcode = models.CharField(max_length=100, unique=True, null=True, blank=True)
    category = models.ForeignKey(
        Category, 
        on_delete=models.PROTECT, #Can't  delete a category that has products
        related_name='products'
    )
    brand = models.CharField(max_length=100, blank=True)
    unit_of_measure = models.CharField(
        max_length=20, 
        choices=UnitofMeasure.choices, 
        default=UnitofMeasure.PIECE
    )
    unit_price_cost = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        validators=[MinValueValidator(0)]
    )
    unit_price_retail = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        validators=[MinValueValidator(0)]
    )
    tax_rate = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=0.00, 
        validators=[MinValueValidator(0)]
    )
    image = models.ImageField(
        upload_to='products/', 
        null=True, 
        blank=True
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta: 
        db_table = 'products'
    
    def __str__(self): 
        return f"{self.name} ({self.sku})"
    
    @property
    def margin(self): 
        """Profit margin - useful in the reports"""
        if self.unit_price_cost > 0: 
            return ((self.unit_price_retail - self.unit_price_cost)/ self.unit_price_retail * 100)
        return 0

class ProductVariant(models.Model):
    """
    For products that come in multiple sizes/weight/colors.
    e.g Fruit juice in 500ml, 1l etc.
    """

    product = models.ForeignKey(
        Product, 
        on_delete=models.CASCADE, 
        related_name='variants'
    )
    variant_label = models.CharField(max_length=100) #e.g "500ml", "red"...
    sku_variant = models.CharField(max_length=100, unique=True) #a unique sku for each variant
    barcode_variant = models.CharField(max_length=100, unique=True, null=True, blank=True)
    price_override = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True, 
        validators=[MinValueValidator(0)]
    )

    class Meta: 
        db_table = 'product_variants'
    
    def __str__(self): 
        return f"{self.product.name} - {self.variant_label}"
