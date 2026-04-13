from django.db import transaction
from django.utils import timezone
from .models import PurchaseOrder, PurchaseOrderItem, GoodsReceipt, GoodsReceiptItem
from apps.stock.models import StockLevel, StockMovement
from apps.batches.models import Batch
from apps.alerts.models import Alert

class PurchaseOrderServices: 

    @staticmethod
    @transaction.atomic
    def receive_goods(purchase_order_id, received_at, items_data, user): 
        """
        The most complex operation in the system. 
        Processes a goods delivery in one atomic transaction.
        If Any step fails, ALL chnages are rolled back.

        Steps: 
        1. Validate PO is in the recievable state
        2. Create GoodsReceipt
        3. For each item: 
            a. Create GoodsReceiptItem
            b. Create or update Batch (with expiry date)
            c. Update StockLevel
            d. Create StockMovement (audit log)
            e. Update PurhchaseOrderItem.quantity_received
        4. Update PO status
        5. Resolve any related LOW_STOCK alerts
        """   

        po = PurchaseOrder.objects.select_for_update().get(
            id=purchase_order_id
        )

        # 1. Validate state
        if po.status not in [
            PurchaseOrder.Status.CONFIRMED, 
            PurchaseOrder.Status.SENT, 
            PurchaseOrder.Status.PARTIALLY_RECEIVED
        ]: 
            raise ValueError(
                f"Cannot receive goods for a PO with status '{po.status}'"
            )
        # 2. Create the GoodsReceipt header
        receipt = GoodsReceipt.objects.create(
            purchase_order=po, 
            received_by=user, 
            received_at=received_at, 
        )

        for item_data in items_data: 
            product_id = item_data['product_id']
            qty_accepted = item_data['quantity_accepted']

            # 3a. Create GoodsReceiptItem
            GoodsReceiptItem.objects.create(
                goods_receipt=receipt, 
                product_id=product_id, 
                batch_number=item_data.get('batch_number', ''), 
                expiry_date=item_data.get('expiry_date'), 
                quantity_received=item_data['quantity_received'], 
                quantity_accepted=qty_accepted, 
                quantity_rejected=item_data.get('quantity_rejected', 0), 
                rejection_reason=item_data.get('rejection_reason', '')
            )

            # 3b. creaete batch repcord if expiry date provided
            if item_data.get('expiry_date') and qty_accepted > 0: 
                Batch.objects.create(
                    product_id=product_id, 
                    location=po.destination_location, 
                    batch_number=item_data.get('batch_number', ''), 
                    expiry_date=item_data['expiry_date'], 
                    manufacture_date=item_data.get('manufacture_date'), 
                    quantity_remaining=qty_accepted, 
                    status=Batch.BatchStatus.ACTIVE
                )
            
            if qty_accepted > 0: 
                # 3c. Update StockLevel - get or create the record
                stock, _ = StockLevel.objects.select_for_update().get_or_create(
                    product_id=product_id, 
                    location=po.destination_location, 
                    defaults={
                        'quantity_on_hand': 0, 
                        'quantity_reserved': 0, 
                        'reorder_point': 0, 
                        'reorder_quantity': 0,
                    }
                )
                stock.quantity_on_hand += qty_accepted
                stock.save()

                # 3d. Create Stockmovements for audit trail
                StockMovement.objects.create(
                    product_id=product_id, 
                    to_location=po.destination_location, 
                    quantity=qty_accepted, 
                    movement_type=StockMovement.MovementType.RECEIVING, 
                    reference_id=f"PO-{po.id}", 
                    performed_by=user, 
                    notes=f"Received via Purchase Order #{po.id}"
                )

                # 3e. Update how much has been received on the PO line
                PurchaseOrderItem.objects.filter(
                    purchase_order=po, 
                    product_id=product_id
                ).update(
                    quantity_received=qty_accepted
                )
        # 4. Update PO status
        all_items = po.items.all()
        all_recieved = all(item.is_fully_recived for item in all_items)
        po.status = (
            PurchaseOrder.Status.RECEIVED if all_recieved
            else PurchaseOrder.Status.PARTIALLY_RECEIVED
        )
        po.save()

        # 5. Resolve LOW_STOCK alerts fro product we just restocked
        received_product_ids = [i['product_d'] for i in items_data]
        Alert.objects.filter(
            location=po.destination_location, 
            type__in=[Alert.AlertType.LOW_STOCK, Alert.AlertType.OUT_OF_STOCK], 
            entity_type='product', 
            entity_id__in=received_product_ids, 
            is_resolved=False
        ).update(
            is_resolved=True, 
            resolved_at=timezone.now()
        )

        return receipt

    @staticmethod
    @transaction.atomic
    def update_status(po_id,new_status, user): 
        """
        Handles status transactions: 
        send, confirm, cancel
        """

        po = PurchaseOrder.objects.select_for_update().get(id=po.id)

        valid_transactions = {
            PurchaseOrder.Status.DRAFT: [
                PurchaseOrder.Status.SENT, 
                PurchaseOrder.Status.CANCELLED
            ], 
            PurchaseOrder.Status.SENT: [
                PurchaseOrder.Status.CONFIRMED, 
                PurchaseOrder.Status.CANCELLED
            ],
            PurchaseOrder.Status.CONFIRMED: [
                PurchaseOrder.Status.CANCELLED
            ], 
        }

        allowed = valid_transactions.get(po.status, [])
        if new_status not in allowed: 
            raise ValueError(
                f"Cannot transition from '{po.status}' to '{new_status}'"
            )
        
        po.status = new_status
        po.save()
        return po