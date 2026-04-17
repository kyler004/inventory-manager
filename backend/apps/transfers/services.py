from django.db import transaction
from django.utils import timezone
from .models import StockTransfer, StockTransferItem
from apps.stock.models import StockLevel, StockMovement

class TransferService:
    
    @staticmethod
    @transaction.atomic
    def dispatch(transfer_id, user): 
        """
        Mark transfer as in transit AND decrement stock
        at the source location immediately.

        We deduct from source on dispatch (not on receipt)
        because the stock has physically left the building.
        It will be in a 'in transit' state until received.
        """

        transfer = StockTransfer.objects.select_for_update().get(
            id=transfer_id
        )

        if transfer.status != StockTransfer.Status.APPROVED: 
            raise ValueError(
                f"Only approved transfers can be dispatch. "
                f"Current status: '{transfer.status}'"
            )

        for item in transfer.items.select_related('product', 'batch'): 
            # Validate enough stock exists before dispatching
            stock = StockLevel.objects.select_for_update().get(
                product=item.product, 
                location=transfer.from_location
            )

            if stock.quantity_available < item.quantity_requested: 
                raise ValueError(
                    f"Insufficient stock for {item.product.name}. "
                    f"Available: {stock.quantity_available}. "
                    f"Requested: {item.quantity_requested}"
                )

            # Decrement source stock
            stock.quantity_on_hand -= item.quantity_requested
            stock.save()

            # Update batch quantity if applicable
            if item.batch: 
                item.batch.quantity_remaining -= item.quantity_requested
                item.batch.save()
            
            #Record the outgoing movement
            StockMovement.objects.create(
                product=item.product, 
                from_location=transfer.from_location, 
                quantity=item.quantity_requested, 
                movement_type=StockMovement.MovementType.TRANSFER_OUT, 
                reference_id=f"TRF-{transfer.id}", 
                performed_by=user, 
                notes=f"Dispatched to {transfer.to_location.name}"
            )

            # Mark how luch was sent 
            item.quantity_sent = item.quantity_requested
            item.save()

        transfer.status = StockTransfer.Status.IN_TRANSIT
        transfer.save()
        return transfer
    
    @staticmethod
    @transaction.atomic
    def receive(transfer_id, received_items_data, user): 
        """
        Confirm reciept at the destination location. 
        Increments stock at the destination and closes the transfer. 

        Note: We allow partial receipts - quantity_received may be less than
        quantity_sent (items lost in transit)
        """

        transfer = StockTransfer.objects.select_for_update().get(
            id=transfer_id
        )

        if transfer.status != StockTransfer.Status.IN_TRANSIT: 
            raise ValueError(
                f"Only in-transit transfers can be received. "
                f"Current status: '{transfer.status}'"
            )
        
        for recieved in received_items_data: 
            item = StockTransferItem.objects.select_for_update().get(
                transfer=transfer, 
                product_id=received['product.id']
            )

            qty_received = received['quantity_received']

            #increment destination stock
            dest_stock,_ = StockLevel.objects.select_for_update().get_or_create(
                product=item.product, 
                location=transfer.to_location, 
                defaults={
                    'quantity_on_hand': 0, 
                    'quantity_reserved': 0, 
                    'reorder_point': 0, 
                    'reorder_quantity': 0, 
                }
            )
            
            dest_stock.quantity_on_hand += qty_received
            dest_stock.save()

            # Record incoming movement at destination
            StockMovement.objects.create(
                product=item.product, 
                to_location=transfer.to_location, 
                batch=item.batch, 
                movement_type=StockMovement.MovementType.TRANSFER_IN, 
                reference_id=f"TRF-{transfer.id}", 
                performed_by=user, 
                notes=f"Received from {transfer.from_location.name}"
            )

            item.quantity_recieved = qty_received 
            item.save()
            transfer.save()
            return transfer
    
    @staticmethod
    @transaction.atomic
    def approve(transfer_id, user): 
        """Warehouse manager approves a requested transfer."""
        transfer = StockTransfer.objects.select_for_update().get(
            id=transfer_id
        )

        if transfer.status != StockTransfer.Status.REQUESTED: 
            raise ValueError(
                "Only requested transfers can be approved."
            )
        
        transfer.status = StockTransfer.Status.APPROVED
        transfer.approved_by = user
        transfer.save()
        return transfer
    
    @staticmethod
    @transaction.atomic
    def cancel(transfer_id, user):
        """
        Cancel a transfer that hasn't been dispatched yet.
        Once IN_TRANSIT, cancellation is not allowed —
        the stock has physically left the source location.
        """
        transfer = StockTransfer.objects.select_for_update().get(
            id=transfer_id
        )

        if transfer.status in [
            StockTransfer.Status.IN_TRANSIT,
            StockTransfer.Status.COMPLETED
        ]:
            raise ValueError(
                "Cannot cancel a transfer that is already in transit or completed."
            )

        transfer.status = StockTransfer.Status.CANCELLED
        transfer.save()
        return transfer
