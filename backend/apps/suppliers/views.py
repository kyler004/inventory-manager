from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Supplier
from .serializers import SupplierSerializer
from apps.users.permissions import IsWarehouseManagerOrAbove

class SupplierViewSet(viewsets.ModelViewSet): 
    queryset = Supplier.objects.filter(is_active=True)
    serializer_class = SupplierSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']: 
            return [IsWarehouseManagerOrAbove()]
        return [IsAuthenticated]
