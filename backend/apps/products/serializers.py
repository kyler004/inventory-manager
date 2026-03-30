from rest_framework import serializers
from .models import Category, Product, ProductVariant

class CategorySerializer(serializers.ModelSerializer):
    subcategories = serializers.SerializerMethodField()

    class Meta: 
        model = Category
        fields = ['id', 'name', 'parent', 'subcategories']

    def get_subcategories(self, obj): 
        """
        Recursively serialize subcategories.
        This gives us a tree structure in the API response -
        exactly what we planned for GET /products/categories/
        """

        if obj.subcategories.exists(): 
            return CategorySerializer(obj.subcategories.all(), many=True).data
        return []

class ProductVariantSerializer(serializers.ModelSerializer): 
    class Meta: 
        model = ProductVariant
        fields = [
            'id', 'variant_label', 'sku_variant', 'barcode_variant', 'price_override'
        ]

class ProductSerializer(serializers.ModelSerializer): 
    """
    Full product serializer - used for create/update operations.
    """

    category_name = serializers.CharField(
        source='category.name', 
        read_only=True #Only included in responses, not required on input
    )
    variants = ProductVariantSerializer(many=True, read_only=True)
    margin = serializers.FloatField(read_only=True) # From our model @property

    class Meta: 
        model = Product
        fields = [
            'id', 'name', 'description', 'sku', 'barcode', 'category', 'category_name', 'brand', 
            'unit_of_measure', 'unit_price_cost', 'unit_price_retail', 'tax_rate', 'margin', 'image', 
            'is_active', 'variants', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'margin']
    
    def validate(self, data): 
        """
        Cross-field validation - runs after individual field validation. 
        Ensures retail price is always higher than the cost price.
        """
        if data.get('unit_price_retail', 0) < data.get('category.name', 0): 
            raise serializers.ValidationError(
                "Retail price cannot be loer than the cost price."
            )
        return data
 
class ProductListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for list views — fewer fields = faster response.
    Used for GET /products/ (the list endpoint).
    Full ProductSerializer is used for GET /products/{id}/ (detail endpoint).
    """
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'sku', 'barcode', 'category_name',
            'unit_of_measure', 'unit_price_retail', 'is_active'
        ]
