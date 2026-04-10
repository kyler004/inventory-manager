from celery import shared_task
from django.db.models import F
from .models import StockLevel
from apps.alerts.services import AlertService
from apps.alerts.models import Alert


@shared_task
def check_low_stock():
    """
    Runs on a schedule (e.g. every hour via Celery Beat).
    Finds all stock levels at or below reorder point
    and creates alerts for each one.
    Connects to: Scenario B from our API design planning.
    """
    low_stock_items = StockLevel.objects.select_related(
        'product', 'location'
    ).filter(
        quantity_on_hand__lte=F('reorder_point'),
        quantity_on_hand__gt=0         # Not completely out
    )

    for item in low_stock_items:
        # Avoid duplicate alerts — check if one already exists
        already_alerted = Alert.objects.filter(
            location=item.location,
            type=Alert.AlertType.LOW_STOCK,
            entity_type='product',
            entity_id=item.product.id,
            is_resolved=False
        ).exists()

        if not already_alerted:
            AlertService.create_and_broadcast(
                location_id=item.location.id,
                alert_type=Alert.AlertType.LOW_STOCK,
                message=(
                    f"{item.product.name} is running low at "
                    f"{item.location.name}. "
                    f"Only {item.quantity_available} {item.product.unit_of_measure} left "
                    f"(reorder point: {item.reorder_point})."
                ),
                entity_type='product',
                entity_id=item.product.id
            )

    out_of_stock = StockLevel.objects.select_related(
        'product', 'location'
    ).filter(quantity_on_hand=0)

    for item in out_of_stock:
        already_alerted = Alert.objects.filter(
            location=item.location,
            type=Alert.AlertType.OUT_OF_STOCK,
            entity_type='product',
            entity_id=item.product.id,
            is_resolved=False
        ).exists()

        if not already_alerted:
            AlertService.create_and_broadcast(
                location_id=item.location.id,
                alert_type=Alert.AlertType.OUT_OF_STOCK,
                message=(
                    f"{item.product.name} is OUT OF STOCK "
                    f"at {item.location.name}."
                ),
                entity_type='product',
                entity_id=item.product.id
            )


@shared_task
def check_expiring_batches():
    """
    Runs nightly at midnight via Celery Beat.
    Finds batches expiring within 7 days.
    Connects to: Scenario C from our API design planning.
    """
    from django.utils import timezone
    from datetime import timedelta
    from apps.batches.models import Batch

    warning_date = timezone.now().date() + timedelta(days=7)

    expiring = Batch.objects.select_related(
        'product', 'location'
    ).filter(
        expiry_date__lte=warning_date,
        expiry_date__gte=timezone.now().date(),
        status=Batch.BatchStatus.ACTIVE
    )

    for batch in expiring:
        already_alerted = Alert.objects.filter(
            location=batch.location,
            type=Alert.AlertType.NEAR_EXPIRY,
            entity_type='batch',
            entity_id=batch.id,
            is_resolved=False
        ).exists()

        if not already_alerted:
            AlertService.create_and_broadcast(
                location_id=batch.location.id,
                alert_type=Alert.AlertType.NEAR_EXPIRY,
                message=(
                    f"Batch {batch.batch_number} of {batch.product.name} "
                    f"expires in {batch.days_until_expiry} days "
                    f"({batch.expiry_date}). "
                    f"{batch.quantity_remaining} units remaining."
                ),
                entity_type='batch',
                entity_id=batch.id
            )

        # Update batch status
        batch.status = Batch.BatchStatus.NEAR_EXPIRY
        batch.save()