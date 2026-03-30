from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
# Create your views here.

from .models import Category, Product
from .serializers import (
    CategorySerializer, ProductSerializer, ProductListSerializer
)
from .filters import ProductFilter
from apps.users.permissions import IsWarehouseManagerOrAbove #Possible bug here 

class CategoryViewSet(viewsets.ModelViewSet):
    """
    Handles all CRUD for categories. 
    GET /products/categories/ -> list
    POST /product/categories -> Create
    GET /products/categories/{id} -> detail
    """

    queryset = Category.objects.filter(parent=None) # Only top-level, subcategories are nested 
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]

class ProductViewSet(viewsets.ModelViewSet): 
    """
    Full CRUD for the products.
    ModelViewSet automatically provides: 
    list, create, retrieve, update, partial_update, destroy
    - matching our API design exactly.
    """

    queryset = Product.objects.select_related('category').prefetch_related('variants')
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ProductFilter
    search_fields = ['name', 'sku', 'barcode', 'brand']
    ordering_fields = ['name', 'unit_price_retail', 'created_at']
    ordering = ['name']

    def get_serializer_class(self):
        """
        Use lightweight serializer for lists, full serializer for everything else.
        This is a performance optimization — list pages don't need all fields.
        """
        if self.action == 'list': 
            return ProductListSerializer
        return ProductSerializer
    
    def get_permissions(self):
       """
        Read operations: any authenticated user
        Write operations: warehouse manager or above
        Matches our permissions matrix from the API design. 
       """
       if self.action in ['create', 'update', 'partial_update', 'destroy']:
           return [IsWarehouseManagerOrAbove()]
       return [IsAuthenticated()]
    
    def destroy(self, request, *args, **kwargs): 
        """
        Overide delete to do a soft delete instead of removong from DB.
        We never lose data - we just mark it inactive.
        """
        product = self.get_object()
        product.is_active = False
        product.save()
        return Reponse(
            {'status': 'success', 'message': 'Product deactivated'}, 
            status=status.HTTP_200_OK
        )
    
    @action(detail=False, methods=['get'], url_path='export')
    def export(self, request):
        """
        GET /products/export/
        Custom action — not part of standard CRUD.
        We'll wire this to django-import-export later.
        """

        #placeholder - will implement with django-import-export
        return Response({'status': 'success', 'message': 'Export coming soon'})