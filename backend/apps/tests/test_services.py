import pytest
from decimal import Decimal
from unittest.mock import patch

from apps.tests.factories import (
    UserFactory, ProductFactory, LocationFactory,
    StockLevelFactory, PurchaseOrderFactory,
    StockTransferFactory
)
from apps.stock.models import StockLevel, StockMovement, StockAdjustment
from apps.stock.services import StockService
from apps.purchase_orders.services import PurchaseOrderService
from apps.purchase_orders.models import PurchaseOrder
from apps.transfers.services import TransferService
from apps.transfers.models import StockTransfer


@pytest.mark.django_db
class TestStockService:

    def test_adjust_stock_updates_quantity(self):
        """
        After adjustment, quantity_on_hand should
        reflect the new value exactly.
        """
        user = UserFactory()
        stock = StockLevelFactory(quantity_on_hand=Decimal('100.00'))

        StockService.adjust_stock(
            product_id=stock.product.id,
            location_id=stock.location.id,
            quantity_after=Decimal('85.00'),
            reason=StockAdjustment.AdjustmentReason.DAMAGE,
            notes='3 units damaged',
            user=user
        )

        stock.refresh_from_db()
        assert stock.quantity_on_hand == Decimal('85.00')

    def test_adjust_stock_creates_movement_record(self):
        """
        Every adjustment must create an immutable movement
        for the audit trail.
        """
        user = UserFactory()
        stock = StockLevelFactory(quantity_on_hand=Decimal('100.00'))

        StockService.adjust_stock(
            product_id=stock.product.id,
            location_id=stock.location.id,
            quantity_after=Decimal('85.00'),
            reason=StockAdjustment.AdjustmentReason.DAMAGE,
            notes='',
            user=user
        )

        movement = StockMovement.objects.get(
            product=stock.product,
            movement_type=StockMovement.MovementType.ADJUSTMENT
        )
        assert movement.quantity == Decimal('15.00')
        assert movement.performed_by == user

    def test_adjust_stock_creates_adjustment_record(self):
        """Adjustment record should capture before and after quantities."""
        user = UserFactory()
        stock = StockLevelFactory(quantity_on_hand=Decimal('100.00'))

        adjustment = StockService.adjust_stock(
            product_id=stock.product.id,
            location_id=stock.location.id,
            quantity_after=Decimal('85.00'),
            reason=StockAdjustment.AdjustmentReason.THEFT,
            notes='',
            user=user
        )

        assert adjustment.quantity_before == Decimal('100.00')
        assert adjustment.quantity_after == Decimal('85.00')
        assert adjustment.reason == StockAdjustment.AdjustmentReason.THEFT

    def test_adjust_stock_raises_if_not_found(self):
        """Adjusting a non-existent stock record should raise an error."""
        user = UserFactory()
        with pytest.raises(StockLevel.DoesNotExist):
            StockService.adjust_stock(
                product_id=99999,
                location_id=99999,
                quantity_after=Decimal('10.00'),
                reason=StockAdjustment.AdjustmentReason.OTHER,
                notes='',
                user=user
            )


@pytest.mark.django_db
class TestPurchaseOrderService:

    def test_receive_goods_updates_stock_level(self):
        """
        Receiving goods should increment quantity_on_hand
        at the destination location.
        """
        from django.utils import timezone
        user = UserFactory()
        location = LocationFactory()
        product = ProductFactory()
        po = PurchaseOrderFactory(destination_location=location)

        from apps.purchase_orders.models import PurchaseOrderItem
        PurchaseOrderItem.objects.create(
            purchase_order=po,
            product=product,
            quantity_ordered=Decimal('50.00'),
            unit_cost=Decimal('1.00')
        )

        PurchaseOrderService.receive_goods(
            purchase_order_id=po.id,
            received_at=timezone.now(),
            items_data=[{
                'product_id': product.id,
                'quantity_received': Decimal('50.00'),
                'quantity_accepted': Decimal('48.00'),
                'quantity_rejected': Decimal('2.00'),
                'rejection_reason': 'Damaged packaging',
            }],
            user=user
        )

        stock = StockLevel.objects.get(
            product=product,
            location=location
        )
        # Only accepted quantity should hit stock
        assert stock.quantity_on_hand == Decimal('48.00')

    def test_receive_goods_creates_stock_movement(self):
        """Goods receipt must generate a RECEIVING movement."""
        from django.utils import timezone
        user = UserFactory()
        location = LocationFactory()
        product = ProductFactory()
        po = PurchaseOrderFactory(destination_location=location)

        from apps.purchase_orders.models import PurchaseOrderItem
        PurchaseOrderItem.objects.create(
            purchase_order=po,
            product=product,
            quantity_ordered=50,
            unit_cost=Decimal('1.00')
        )

        PurchaseOrderService.receive_goods(
            purchase_order_id=po.id,
            received_at=timezone.now(),
            items_data=[{
                'product_id': product.id,
                'quantity_received': 50,
                'quantity_accepted': 50,
                'quantity_rejected': 0,
            }],
            user=user
        )

        assert StockMovement.objects.filter(
            product=product,
            movement_type=StockMovement.MovementType.RECEIVING
        ).exists()

    def test_receive_goods_invalid_status_raises(self):
        """
        Cannot receive goods on a DRAFT PO.
        Status must be CONFIRMED or SENT.
        """
        from django.utils import timezone
        user = UserFactory()
        po = PurchaseOrderFactory(status=PurchaseOrder.Status.DRAFT)

        with pytest.raises(ValueError, match="Cannot receive goods"):
            PurchaseOrderService.receive_goods(
                purchase_order_id=po.id,
                received_at=timezone.now(),
                items_data=[],
                user=user
            )


@pytest.mark.django_db
class TestTransferService:

    def test_dispatch_decrements_source_stock(self):
        """Dispatching a transfer should reduce source location stock."""
        user = UserFactory()
        product = ProductFactory()
        source = LocationFactory()
        destination = LocationFactory()

        stock = StockLevelFactory(
            product=product,
            location=source,
            quantity_on_hand=Decimal('100.00'),
            quantity_reserved=Decimal('0.00')
        )

        transfer = StockTransferFactory(
            from_location=source,
            to_location=destination,
            status=StockTransfer.Status.APPROVED
        )

        from apps.transfers.models import StockTransferItem
        StockTransferItem.objects.create(
            transfer=transfer,
            product=product,
            quantity_requested=Decimal('30.00'),
            quantity_sent=Decimal('0.00'),
            quantity_received=Decimal('0.00')
        )

        TransferService.dispatch(transfer.id, user)

        stock.refresh_from_db()
        assert stock.quantity_on_hand == Decimal('70.00')

    def test_dispatch_fails_insufficient_stock(self):
        """
        Cannot dispatch more than what's available.
        Error must be raised BEFORE any DB changes happen.
        """
        user = UserFactory()
        product = ProductFactory()
        source = LocationFactory()

        StockLevelFactory(
            product=product,
            location=source,
            quantity_on_hand=Decimal('10.00'),   # Only 10 available
            quantity_reserved=Decimal('0.00')
        )

        transfer = StockTransferFactory(
            from_location=source,
            status=StockTransfer.Status.APPROVED
        )

        from apps.transfers.models import StockTransferItem
        StockTransferItem.objects.create(
            transfer=transfer,
            product=product,
            quantity_requested=Decimal('50.00'),  # Requesting 50 — should fail
            quantity_sent=Decimal('0.00'),
            quantity_received=Decimal('0.00')
        )

        with pytest.raises(ValueError, match="Insufficient stock"):
            TransferService.dispatch(transfer.id, user)

        # Verify stock was NOT modified (transaction rolled back)
        stock = StockLevel.objects.get(product=product, location=source)
        assert stock.quantity_on_hand == Decimal('10.00')

    def test_cancel_blocked_when_in_transit(self):
        """
        Once in transit, a transfer cannot be cancelled —
        stock has already physically left the source.
        """
        user = UserFactory()
        transfer = StockTransferFactory(
            status=StockTransfer.Status.IN_TRANSIT
        )

        with pytest.raises(ValueError, match="in transit"):
            TransferService.cancel(transfer.id, user)