from django.db import models

class Location(models.Model): 
    """
    Represents any physical place that holds stock.
    From our planning - Module 2: Locations & warehouses.
    Could be a warehouse, a store branch, or a transit point.
    """

    class LocationType(models.TextChoices):
        WAREHOUSE = 'warehouse', 'Warehouse'
        STORE = 'store', 'Store'
        TRANSIT = 'transit', 'Transit'

    name = models.CharField(max_length=200)
    type = models.CharField(
        max_length=20, 
        choices=LocationType.choices,
        default=LocationType.STORE
    )
    address = models.TextField(blank=True)
    manager = models.ForeignKey(
        'users.User', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='managed_locations'
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta: 
        db_table = 'locations'
    
    def __str__(self):
        return f"{self.name} ({self.get_type_display()})"

class Zone(models.Model): 

    """
    A sub-area wothun a location e.g Aisle 3, Cold Room 8
    Helps with precisestock placement tracking
    """
    
    class ZoneType(models.TextChoices): 
        SHELF = 'shelf', 'Shelf'
        FRIDGE = 'fridge', 'Fridge'
        FREEZER = 'freezer', 'Freezer'
        BACKROOM = 'backroom', 'Backroom'

    location = models.ForeignKey(
        Location, 
        on_delete=models.CASCADE, 
        related_name='zones'
    )
    name = models.CharField(max_length=100)
    zone_type = models.CharField(
        max_length=20, 
        choices=ZoneType.choices, 
        default=ZoneType.SHELF
    )

    class Meta:
        db_table = 'zones'
        unique_together = ['location', 'name'] #No two zones with the same name in the same location
    
    def __str__(self): 
        return f"{self.location.name}  - {self.name}"