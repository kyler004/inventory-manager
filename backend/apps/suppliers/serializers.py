from rest_framework import serializers
from .models import Supplier, SupplierProduct


class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = [
            'id', 'name', 'contact_person', 'email',
            'phone', 'address', 'payment_terms',
            'lead_time_days', 'is_active', 'created_at'
        ]


class SupplierProductSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(
        source='product.name',
        read_only=True
    )

    class Meta:
        model = SupplierProduct
        fields = [
            'id', 'supplier', 'product', 'product_name',
            'supplier_sku', 'unit_cost',
            'minimum_order_quantity', 'is_preferred_supplier'
        ]