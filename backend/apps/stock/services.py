from decimal import Decimal
from django.db import models
from django.db import transaction
from django.utils import timezone
from .models import StockLevel, StockMovement, StockAdjustment


class StockService:
    """
    All stock business logic lives here — NOT in views.
    Views just call these methods and return the result.
    This makes logic reusable and independently testable.
    """

    @staticmethod
    @transaction.atomic
    def adjust_stock(product_id, location_id, quantity_after, reason, notes, user):
        """
        Performs a manual stock adjustment.
        1. Locks the stock row (prevents race conditions)
        2. Records before/after quantities
        3. Creates an adjustment record
        4. Creates a stock movement for the audit log
        5. Updates the stock level
        All in one atomic transaction — either everything succeeds or nothing does.
        """
        stock = StockLevel.objects.select_for_update().get(
            product_id=product_id,
            location_id=location_id
        )

        quantity_before = stock.quantity_on_hand
        quantity_change = quantity_after - quantity_before

        # Create the formal adjustment record
        adjustment = StockAdjustment.objects.create(
            product_id=product_id,
            location_id=location_id,
            quantity_before=quantity_before,
            quantity_after=quantity_after,
            reason=reason,
            notes=notes,
            performed_by=user
        )

        # Create the immutable movement log entry
        StockMovement.objects.create(
            product_id=product_id,
            to_location_id=location_id if quantity_change > 0 else None,
            from_location_id=location_id if quantity_change < 0 else None,
            quantity=abs(quantity_change),
            movement_type=StockMovement.MovementType.ADJUSTMENT,
            reference_id=f"ADJ-{adjustment.id}",
            performed_by=user,
            notes=notes
        )

        # Update the actual stock level
        stock.quantity_on_hand = quantity_after
        stock.save()

        return adjustment

    @staticmethod
    def get_low_stock_items(location_id=None):
        """
        Returns all stock levels where available quantity
        is at or below the reorder point.
        Used by Celery tasks and the GET /stock/low/ endpoint.
        """
        queryset = StockLevel.objects.select_related(
            'product', 'location'
        ).filter(
            quantity_on_hand__lte=models.F('reorder_point')
        )
        if location_id:
            queryset = queryset.filter(location_id=location_id)
        return queryset