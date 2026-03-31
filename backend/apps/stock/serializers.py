from rest_framework import serializers
from .models import StockLevel, StockMovement, StockAdjustment
from apps.products.serializers import ProductListSerializer
from apps.locations.serializers import LocationSerializer

class StockLevelSerializer(serializers.ModelSerializer): 
    product = ProductListSerializer(read_only=True)
    location_name = serializers.CharField(source='location.name', read_only=True)
    quantity_available = serializers.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        read_only=True #computed property from the model
    )
    stock_status = serializers.CharField(read_only=True) # OK/ LOW/ OUT

    class Meta: 
        model = StockLevel
        fields = [
            'id', 'product', 'location', 'location_name', 'zone', 'quantity_on_hand', 'quantity_reserved', 
            'reorder_point', 'reorder_quantity', 'max_stock_level', 'stock_status', 'last_updated'
        ]

class StockMovementSerializer(serializers.ModelSerializer): 
    product_name = serializers.CharField(source='product.name', read_only=True)
    performed_by_name = serializers.CharField(source='performed_by.name', read_only=True)

    class Meta: 
        model = StockMovement
        fields = [
           'id', 'product', 'product_name', 'from_location',
            'to_location', 'batch', 'quantity', 'movement_type',
            'reference_id', 'performed_by', 'performed_by_name',
            'notes', 'created_at' 
        ]
        read_only_fields = ['performed_by', 'created_by']

class StockAdjustmentSerializer(serializers.ModelSerializer):
    """
    Used for POST /stock/adjust/
    The view will call StockService to handle the actual DB logic.
    """

    quantity_change = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True  # Computed from before/after
    )

    class Meta:
        model = StockAdjustment
        fields = [
            'id', 'product', 'location', 'quantity_before',
            'quantity_after', 'quantity_change', 'reason',
            'notes', 'performed_by', 'approved_by', 'created_at'
        ]
        read_only_fields = ['performed_by', 'quantity_before', 'created_at']