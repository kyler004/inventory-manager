from django.db.models import (
    Sum, Count, Avg, F, Q, 
    ExpressionWrapper, DecimalField
)

from django.db.models.functions import TruncMonth, TruncDate
from django.utils import timezone
from datetime import timedelta

from apps.stock.models import StockLevel, StockMovement, StockAdjustment
from apps.batches.models import Batch
from apps.purchase_orders.models import PurchaseOrder, GoodsReceiptItem

class StockValuationReport: 
    """
    Total inventory value = quantity_on_hand x unit_price_cost
    Broken down by location and category.
    Answers: "How much is our current stock worth?"
    """

    @staticmethod
    def generate(location_id=None, category_id=None): 
        queryset = StockLevel.objects.select_related(
            'product__category', 'location'
        ).filter(quantity_on_hand__gt=0)

        if location_id: 
            queryset = queryset.filter(location_id=location_id)
        if category_id: 
            queryset = queryset.filter(product__category_id=category_id)

        #Annotate each row with its value
        queryset = queryset.annotate(
            stock_value=ExpressionWrapper(
                F('quantity_on_hand') * F('product__unit_price_cost'), 
                output_field=DecimalField()
            ), 
            retail_value=ExpressionWrapper(
                F('quantity_on_hand') * F('product__unit_price_retail'), 
                output_field=DecimalField()
            )
        )

        # Group by location
        by_location = queryset.values(
            'location__name'
        ).annotate(
            total_cost_value=Sum('stock_value'), 
            total_retail_value=Sum('retail_value'), 
            product_count=Count('product', distinct=True)
        ).order_by('-total_cost_value')

        # Group by category
        by_category = queryset.values(
            'product__category__name'
        ).annotate(
            total_cost_value=Sum('stock_value'), 
            total_retail_value=Sum('retail_value'), 
            product_count=Count('product', distinct=True)
        ).order_by('-total_cost_value')

        # Overall totals
        totals = queryset.aggregate(
            total_cost_value=Sum('stock_value'), 
            total_retail_value=Sum('retail_value'), 
            total_products=Count('product', distinct=True)
        )

        return {
            'totals': totals, 
            'by_location': list(by_location), 
            'by_category': list(by_category), 
        }

class ShrinkageReport: 
    """
    Tracks inventory losses from adjustments over time.
    Answers: "How much stock are we losing and why?"
    """

    @staticmethod
    def generate(location_id=None, date_from=None, date_to=None): 
        queryset = StockAdjustment.objects.select_related(
            'product', 'location', 'performed_by'
        ).filter(
            # Only negative adjustments = losses
            quantity_after__lt=F('quantity_before')
        )

        if location_id: 
            queryset = queryset.filter(location_id=location_id)
        if date_from: 
            queryset = queryset.filter(created_at__date__gte=date_from)
        if date_to: 
            queryset = queryset.filter(created_at__date__lte=date_to)

        #  Total loss values
        queryset = queryset.annotate(
            loss_quantity=ExpressionWrapper(
                F('quantity_before') - F('quantity_after'), 
                output_field=DecimalField()
            ), 
            loss_value=ExpressionWrapper(
                (F('quantity_before') - F('quantity_after'))
                 * F("product__unit_price_cost"), 
                 output_field=DecimalField()
            )
        )

        # Group by reason
        by_reason = queryset.values('reason').annotate(
            total_incidents=Count('id'), 
            total_loss_value=Sum('loss_value'), 
            total_loss=Sum('loss_quantity')
        ).order_by('-total_loss_value')

        # Group by product  - which products are shrinking the most?
        by_product = queryset.values(
            'product__name', 'product__sku'
        ).annotate(
            total_incidents=Count('id'), 
            total_loss=Sum('loss_value'), 
            total_loss_quantity=Sum('loss_quantity')
        ).order_by('-total_loss_value')[:10] #Top 10

        totals = queryset.aggregate(
            total_incidents=Count('id'), 
            total_loss_value=Sum('loss_value'), 
        )

        return {
            'totals': totals,
            'by_reason': list(by_reason), 
            'by_product': list(by_product), 
        }
    
class InventoryTurnoverReport: 
    """
    Turnover rate = units sold / average stock level.
    High turnover = selling fast (good).
    Low turnover = slow moving stock (capital tied up).
    Answers: "Which products are moving and which are sitting?"
    """

    @staticmethod
    def generate(location_id=None, days=30): 
        date_from = timezone.now() - timedelta(days=days)

        # Total units sold per product in period

        sales = StockMovement.objects.filter(
            movement_type=StockMovement.MovementType.SALE, 
            created_at__gte=date_from
        )

        if location_id: 
            sales = sales.filter(from_location_id=location_id)
        
        sold_by_product = sales.values(
            'product__id', 'product__name', 'product__sku'
        ).annotate(
            units_sold=Sum('quantity')
        ).order_by('-units_sold')

        #Add current stock level to each product 
        result = []
        for row in sold_by_product: 
            stock = StockLevel.objects.filter(
                product_id=row['product__id']
            )
            if location_id: 
                stock = stock.filter(location_id=location_id)
            
            avg_stock = stock.aggregate(
                vag=Avg('quantity_on_hand')
            )['avg'] or 0

            turnover_rate = (
                float(row['units_sold']) / float(avg_stock)
                if avg_stock > 0 else 0
            )

            result.append({
                'product_id': row['product__id'], 
                'product_name': row['product__name'],
                'product__sku': row['product__sku'], 
                'units_sold': row['units_sold'], 
                'avg_stock_level': round(avg_stock, 2), 
                'turnover_rate': round(turnover_rate, 2), 
            })
        
        return {
            'period_days': days, 
            'products': result
        }
    
class DeadStockReport: 
    """
    Products with no outgoigng movement on N days.
    Answers: "What stock should we consider discounting or returning?"
    """

    @staticmethod
    def generate(location_id=None, days=30): 
        cutoff_date = timezone.now() - timedelta(days=days)

        # Products that HAVE moved recently
        active_product_ids = StockMovement.objects.filter(
            created_at__gte=cutoff_date, 
            movement_type=StockMovement.MovementType.SALE
        ).values_list('product_id', flat=True).distinct()

        #Stock levels for products that HAVE not moved 
        dead_stock = StockLevel.objects.select_related(
            'product__category', 'location'
        ).filter(
            quantity_on_hand__gt=0
        ).exclude(
            product_id__in=active_product_ids
        )

        if location_id: 
            dead_stock = dead_stock.filter(location_id=location_id)

        dead_stock = dead_stock.annotate(
            stock_value=ExpressionWrapper(
                F('quantity_on_hand') * F('product__unit_price_cost'), 
                output_field=DecimalField()
            )
        )

        return {
            'days_threshold': days, 
            'total_dead_stock_value': dead_stock.aggregate(
                total=Sum('stock_value')
            )['total'] or 0, 
            'items': list(dead_stock.values(
                'product__name', 'product__sku', 
                'product__category__name', 
                'location__name', 
                'quantity_on_hand', 'stock_value'
            ).order_by('-stock_value'))
        }

class SupplierPerformanceReport:
    """
    Measures supplier reliability.
    Answers: "Which suppliers deliver on time with good quality?"
    """

    @staticmethod
    def generate(date_from=None, date_to=None):
        orders = PurchaseOrder.objects.filter(
            status=PurchaseOrder.Status.RECEIVED
        ).select_related('supplier')

        if date_from:
            orders = orders.filter(order_date__gte=date_from)
        if date_to:
            orders = orders.filter(order_date__lte=date_to)

        result = []
        for order in orders:
            receipts = GoodsReceiptItem.objects.filter(
                goods_receipt__purchase_order=order
            ).aggregate(
                total_received=Sum('quantity_received'),
                total_accepted=Sum('quantity_accepted'),
                total_rejected=Sum('quantity_rejected')
            )

            total_received = receipts['total_received'] or 0
            total_rejected = receipts['total_rejected'] or 0
            rejection_rate = (
                float(total_rejected) / float(total_received) * 100
                if total_received > 0 else 0
            )

            result.append({
                'supplier_id': order.supplier.id,
                'supplier_name': order.supplier.name,
                'po_id': order.id,
                'order_date': order.order_date,
                'expected_date': order.expected_delivery_date,
                'total_accepted': total_accepted,
                'rejection_rate': round(rejection_rate, 2),
            })

        return {'orders': result}