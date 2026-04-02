from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import StockLevel, StockMovement, StockAdjustment
from .serializers import (
    StockLevelSerializer, StockMovementSerializer, StockAdjustmentSerializer
)
from .services import StockService
from apps.users.permissions import IsStoreManagerOrAbove


class StockLevelViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Stock levels are READ ONLY through this viewset.
    They can only be changed through controlled operations:
    adjustments, transfers, goods receipts.
    This protects data integrity.
    """
    serializer_class = StockLevelSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['location', 'product']

    def get_queryset(self):
        """
        Admins see all locations.
        Other users only see their own location's stock.
        """
        user = self.request.user
        queryset = StockLevel.objects.select_related(
            'product', 'location', 'zone'
        )
        if user.role.name != 'Admin':
            queryset = queryset.filter(location=user.location)
        return queryset

    @action(detail=False, methods=['get'], url_path='low')
    def low_stock(self, request):
        """GET /stock/low/ — products below reorder point."""
        location_id = request.query_params.get('location')
        items = StockService.get_low_stock_items(location_id)
        serializer = self.get_serializer(items, many=True)
        return Response({'status': 'success', 'data': serializer.data})

    @action(detail=False, methods=['get'], url_path='out')
    def out_of_stock(self, request):
        """GET /stock/out/ — products with zero available stock."""
        queryset = self.get_queryset().filter(quantity_on_hand=0)
        serializer = self.get_serializer(queryset, many=True)
        return Response({'status': 'success', 'data': serializer.data})


class StockAdjustmentViewSet(viewsets.ModelViewSet):
    """Handles POST /stock/adjust/ and GET /stock/adjustments/"""
    serializer_class = StockAdjustmentSerializer
    permission_classes = [IsStoreManagerOrAbove]

    def get_queryset(self):
        return StockAdjustment.objects.select_related(
            'product', 'location', 'performed_by'
        )

    def create(self, request, *args, **kwargs):
        """
        Delegates to StockService — the view stays thin.
        No business logic here.
        """
        try:
            adjustment = StockService.adjust_stock(
                product_id=request.data.get('product_id'),
                location_id=request.data.get('location_id'),
                quantity_after=request.data.get('quantity_after'),
                reason=request.data.get('reason'),
                notes=request.data.get('notes', ''),
                user=request.user
            )
            serializer = self.get_serializer(adjustment)
            return Response(
                {'status': 'success', 'data': serializer.data},
                status=status.HTTP_201_CREATED
            )
        except StockLevel.DoesNotExist:
            return Response(
                {'status': 'error', 'message': 'Stock record not found.'},
                status=status.HTTP_404_NOT_FOUND
            )


class StockMovementViewSet(viewsets.ReadOnlyModelViewSet):
    """
    GET /stock/movements/ — read-only audit log.
    Nobody can create, edit or delete movements directly.
    They are only created by other services (adjust, receive, transfer).
    """
    serializer_class = StockMovementSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['product', 'movement_type', 'from_location', 'to_location']
    ordering = ['-created_at']

    def get_queryset(self):
        return StockMovement.objects.select_related(
            'product', 'from_location', 'to_location', 'performed_by'
        )