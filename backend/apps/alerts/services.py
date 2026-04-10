from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import Alert


class AlertService:
    """
    Creates alerts in the database AND broadcasts
    them via WebSocket in one single call.
    Celery tasks and views both use this.
    """

    @staticmethod
    def create_and_broadcast(
        location_id,
        alert_type,
        message,
        entity_type='',
        entity_id=None
    ):
        # 1. Save to database (persistent record)
        alert = Alert.objects.create(
            location_id=location_id,
            type=alert_type,
            message=message,
            entity_type=entity_type,
            entity_id=entity_id
        )

        # 2. Broadcast via WebSocket (real-time delivery)
        channel_layer = get_channel_layer()

        payload = {
            'type': 'send_alert',   # Must match consumer method name
            'payload': {
                'id': alert.id,
                'alert_type': alert_type,
                'message': message,
                'entity_type': entity_type,
                'entity_id': entity_id,
                'created_at': alert.created_at.isoformat(),
            }
        }

        # Send to location-specific group
        async_to_sync(channel_layer.group_send)(
            f'alerts_location_{location_id}',
            payload
        )

        # Also send to global admin group
        async_to_sync(channel_layer.group_send)(
            'alerts_global',
            payload
        )

        return alert