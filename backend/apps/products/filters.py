import django_filters
from .models import Product

class ProductFilter(django_filters.FilterSet): 
    """
    Enables URL filtering like: 
    GET /products/?category=5&is_active=true&min_price=1.00
    Connects to our API design's filtering convention
    """

    min_price = django_filters.NumberFilter(
        field_name = 'unit_price_retail', 
        lookup_expr='gte' #Greater than or equal
    )
    max_price = django_filters.NumberFilter(
        field_name='unit_price_retail', 
        lookup_expr='lte' #Less than or equals to
    )
    category = django_filters.NumberFilter(field_name='category__id')

    class Meta: 
        model = Product
        fields = ['is_active' ,'brand', 'measure']