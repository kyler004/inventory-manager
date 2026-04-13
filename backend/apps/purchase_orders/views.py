from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import PurchaseOrder
from .serializers import PurchaseOrderSerializer, GoodsReceiptSerializer
from .services import PurchaseOrderServices
from apps.users.permissions import IsWarehouseManagerOrAbove

# Create your views here.
class PurchaseOrderViewSet(viewsets.ModelViewSet): 
    serializer_class = PurchaseOrderSerializer
    permission_classes = [IsWarehouseManagerOrAbove]
    filterset_fields = ['status', 'supplier']
    ordering = ['-created_at']

    def get_queryset(self):
        return PurchaseOrder.objects.select_related(
            'supplier', 'destination_location', 'created_by'
        ).prefetch_related('items__product')

    def perform_create(self, serializer):
        """Automatically attach the logged-in user as creator."""
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def send(self, request, pk=None): 
        """POST /purchase-orders/{id}/send/"""
        return self._transition(pk, PurchaseOrder.Status.SENT, request.user)
    
    @action(detail=True, methods=['post'])
    def confirm(self, request, pk=None): 
        """POST /purchase-orders/{id}/confirm/"""
        return self._transition(pk, PurchaseOrder.Status.CONFIRMED, request.user)
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None): 
        """POST /purchase-orders/{id}/cancel/"""
        return self._transition(pk, PurchaseOrder.Status.CANCEL, request.user)
    
    @action(detail=True, methods=['post'])
    def received(self, request, pk=None): 
        """
        POST /purchase-orders/{id}/receive/
        The big one - triggers the full receive_goods transaction.
        """
        try: 
            receipt = PurchaseOrderServices.receive_goods(
                purchase_order_id=pk, 
                received_at=request.data.get('received_at'), 
                items_data=request.data.get('items', []), 
                user=request.user 
            )
            serializer = GoodsReceiptSerializer(receipt)
            return Response(
                {'status': 'success', 'message': serializer.data}, 
                status=status.HTTP_201_CREATED
            )
        except ValueError as e: 
            return Response(
                {'status': 'error', 'message': str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def _transition(self, pk, new_status, user):
        """Helper to avoid repeating transition logic in every action. """
        try: 
            po = PurchaseOrderServices.update_status(pk, new_status, user)
            serializer = self.get_serializer(po)
            return Response({'status': 'success', 'data': serializer.data})
        except ValueError as e: 
            return Response(
                {'status': 'error', 'message': str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )
