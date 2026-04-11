from rest_framework import serializers
from .models import (
    PurchaseOrder, PurchaseOrderItem, 
    GoodsReceipt, GoodsReceiptItem
)

class PurchaseOrderItemSerializer(serializers.ModelSerializer): 
    product_name = serializers.CharField(
        source='product.name', 
        read_only=True
    )
    subtotal = serializers.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        read_only=True #Computed @property from model
    )
    is_fully_received = serializers.BooleanField(read_only=True)

    class Meta: 
        model = PurchaseOrderItem
        fields = [
            'id', 'product', 'product_name', 'quantity_ordered', 
            'quantity_received', 'unit_cost', 'subtotal', 
            'is_fully_received'
        ]

class PurchaseOrderSerializer(serializers.ModelSerializer): 
    items = PurchaseOrderItemSerializer(many=True)
    supplier_name = serializers.CharField(
        source='supplier.name', 
        read_only=True
    )
    destination_name = serializers.CharField(
        source='destination_location.name', 
        read_only=True
    )

    class Meta: 
        model = PurchaseOrder
        fields = [
            'id', 'supplier', 'supplier_name', 'destination_location', 
            'destination_name', 'status', 'order_date', 'expected_delivery_date', 
            'total_amount', 'notes', 'items', 'created_by', 'created_at'
        ]
        read_only_fields = ['created_by', 'order_date', 'created_at', 'status']

        def create(self, validate_data): 
            """
            Handle nested creation - items are created alongside the purchase order. 
            DRF doesn't handle nested writes automatically.
            """

            items_data = validate_data.pop('items')
            po = PurchaseOrder.objects.create(**validate_data)

            total = 0
            for item_data in items_data: 
                item = PurchaseOrderItem.objects.create(
                    purchase_order=po, 
                    **items_data
                )
                total += item.subtotal
            
            # Calculate and save total amount
            po.total_amount = total
            po.save()

            return po
        
class GoodsRecieptItemSerializer(serializers.ModelSerializer): 
    class Meta:
        model = GoodsReceiptItem
        fields = [
            'id', 'product', 'batch_number', 'expiry_date', 
            'quantity_recieved', 'quantity_accepted', 'quantity_rejected', 
            'rejection_reason'
        ]

class GoodsReceiptSerializer(serializers.ModelSerializer): 
    items = GoodsRecieptItemSerializer(many=True)

    class Meta: 
        model = GoodsReceipt
        fields = ['id', 'purchase_order', 'recieved_at', 'notes', 'items']