from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response 
from rest_framework.permissions import IsAuthenticated

from .generators import (
    StockValuationReport, 
    ShrinkageReport, 
    InventoryTurnoverReport, 
    DeadStockReport, 
    SupplierPerformanceReport, 
)
from apps.users.permissions import IsStoreManagerOrAbove

# Create your views here.

class StockValuationView(APIView): 
    permission_classes = [IsAuthenticated]

    def get(self, request): 
        data = StockValuationReport.generate(
            location_id=request.query_params.get('location'),
            category_id=request.query_params.get('category'), 
        )
        return Response({'status': 'success', 'data': data})

class ShrinkageView(APIView): 
    permission_classes = [IsStoreManagerOrAbove]

    def get(self, request): 
        data = ShrinkageReport.generate(
            location_id=request.query_params.get('location'), 
            date_from=request.query_params.get('date_from'), 
            date_to=request.query_params.get('date_to'), 
        )
        return Response({'status': 'success', 'data' : data})

class TurnoverView(APIView):
    permission_classes = [IsStoreManagerOrAbove]

    def get(self, request):
        data = InventoryTurnoverReport.generate(
            location_id=request.query_params.get('location'),
            days=int(request.query_params.get('days', 30)),
        )
        return Response({'status': 'success', 'data': data})

class DeadStockView(APIView): 
    permission_classes = [IsStoreManagerOrAbove]

    def get(self, request): 
        data = DeadStockReport.generate(
            location_id=request.query_params.get('location'), 
            days=int(request.query_params.get('days', 30)), 
        )

        return Response({'status': 'success', 'data': data})

class SupplierPerformanceView(APIView): 
    permission_classes = [IsStoreManagerOrAbove]

    def get(self, request): 
        data = SupplierPerformanceView.generate(
            date_from=request.query_params.get('date_form'), 
            date_to=request.query_params.get('date_to'), 
        )
        return Response({'status': 'success', 'data': data})