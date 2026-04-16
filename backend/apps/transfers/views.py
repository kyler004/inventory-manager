from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import StockTransfer
from .serializers import StockTransferSerializer
from .services import TransferService
from apps.users.permissions import IsStoreManagerOrAbove, IsWarehouseManagerOrAbove

# Create your views here.

class StockTransferViewSet(viewsets.ModelViewSet): 
    serializer_class = StockTransferSerializer
    filterset_fields = ['status', 'from_location', 'to_location']
    ordering = ['-created_at']

    def get_queryset(self):
        user = self.request.user
        queryset = StockTransfer.objects.select_related(
            'from_location', 'to_location'
            'request_by', 'approved_by'
        ).prefetch_related('item__product')

        # Non admins only see transfers involving their location

        if user.role.name != 'Admin': 
            queryset = queryset.filter(
                from_location=user.location
            ) | queryset.filter(
                to_location=user.location
            )

        return queryset
    
    def get_permissions(self):
        if self.action in ['approve']:
            return [IsWarehouseManagerOrAbove]
        return [IsStoreManagerOrAbove]

    def perform_create(self, serializer):
        serializer.save(requested_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None): 
        """POST /transfers/{id}/approve/"""
        return self._run_service(
            TransferService.approve, pk, request.user
        )
    
    @action(detail=True, methods=['post'])
    def dispatch(self, request, pk=None):
        return self._run_service(
            TransferService.dispatch, pk, request.user
        )
    
    @action(detail=True, methods=['post'])
    def receive(self, request, pk=None): 
        """POST /transfers/{id}/receive/"""

        try: 
            transfer = TransferService.receive(
                transfer_id=pk, 
                recieved_items_data=request.data.get('items', []), 
                user=request.user
            )
            serializer = self.get_serializer(transfer)
            return Response({'status': 'success', 'data': serializer.data})
        except (ValueError, Exception) as e: 
            return Response(
                {'status': 'error', 'message': str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        @action(detail=True, methods=['post'])
        def cancel(self, request, pk=None): 
            """POST /transfers/{id}/cancel/"""
            return self._run_service(
                TransferService.cancel, pk, request.user
            )
        
        def _run_service(self, service_fn, pk, user):
            """
            Generic helper — runs a service function and
            wraps the result in our standard response envelope.
            Keeps all action methods clean and DRY.
            """
            try:
                transfer = service_fn(pk, user)
                serializer = self.get_serializer(transfer)
                return Response({'status': 'success', 'data': serializer.data})
            except ValueError as e:
                return Response(
                    {'status': 'error', 'message': str(e)},
                    status=status.HTTP_400_BAD_REQUEST
                )