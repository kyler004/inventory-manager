from rest_framework import serializers
from .models import StockTransfer, StockTransferItem

class StockTransformItemSerializer(serializers.ModelSerializer): 
    product_name = serializers.CharField(
        source='product.name', 
        read_only=True
    )
    batch_number = serializers.CharField(
        source='batch.batch_number', 
        read_only=True
    )

    class Meta: 
        model = StockTransferItem
        fields = [
            'id', 'product', 'product_name', 'batch', 
            'batch_number', 'quantity_requested', 
            'quantity_sent', 'quantity_received'
        ]

class StockTransferSerializer(serializers.ModelSerializer): 
    items = StockTransformItemSerializer(many=True)
    from_location_name = serializers.CharField(
        source='from_location.name', 
        read_only=True
    )
    to_location_name = serializers.CharField(
        source='to_location.name', 
        read_only=True
    )
    requested_by_name = serializers.CharField(
        source='requested_by.name', 
        read_only=True
    )

    class Meta: 
        model = StockTransfer
        fields = [
            'id', 'from_locations','from_location_name', 
            'to_location', 'to_location_name', 'status', 
            'requested_by', 'requested_by_name', 'approved_by', 
            'notes', 'items', 'created_at', 'completed_at'
        ]
        read_only_fields = [
            'status', 'requested_by', 'approved_by', 'created_at',
            'completed_at' 
        ] 

        def validate(self, data): 
            """
            Can't transfer stock to the samelocation it came from.
            Catches a logical error before it touches the database.
            """
            if data.get('from_location') == data.get('to_location'): 
                raise serializers.ValidationError(
                    "Souce and destination cannot be the same."
                )
            return data
        
        def create(self, validated_data): 
            """Handle nested item creation alongside the transfer."""
            items_data = validated_data.pop('items')
            transfer = StockTransfer.objects.create(**validated_data)

            for item_data in items_data: 
                StockTransferItem.objects.create(
                    transfer=transfer, 
                    **item_data
                )
            return transfer