import json
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
from rest_framework_simplejwt.tokens import AccessToken
from django.contrib.auth import get_user_model

User = get_user_model()

class AlertConsumer(AsyncJsonWebsocketConsumer): 
    """
    Handles Websocket connections for real-time alerts.
    Each user joins a group tied to their location - 
    so a manager at Branch A only gets alerts for branch A. 
    Connects to the planning: wss://api.yourstore.com/ws/alerts/
    """

    async def connect(self):
        """Called when a client opens a websocket connection."""
       
        # Authenticate via token in query string
        # e.g wss://localhost:8000/ws/alerts/?token=eYj... 
        # (°>-<) have no idea of why I used this instead of docstrings

        token = self._get_token_from_query()

        if not token: 
            await self.close(code=4001)
            return 
        
        user = await self.get_user_from_token(token)

        if not user: 
            await self.close(code=4001)
            return
        
        self.user = user

        # Each location gets its own channel group
        # Admins join a general group to see each others alerts

        if user.role and user.role.name == 'Admin': 
            self.group_name = 'alerts_global'
        else: 
            self.group_name = f'alerts_location_{user.location_id}'
        
        # Join the group
        await self.channel_layer.group_add(
            self.group_name, 
            self.channel_name
        )

        await self.accept()

        # send any unresolved alerts immediately on connect
        unresolved = await self.get_unresolved_alerts()
        await self.send(send_data=json.dumps({
            'type': 'initial_alerts', 
            'alerts': unresolved
        }))

    async def disconnect(self, text_data): 
        """
        Called when a message is recieved FROM the client, 
        We use this to handle alert resolution from the UI.
        """

        data = json.loads(text_data)

        if data.get('type') == 'resolve_alert': 
            await self.resolve_alert(data.get('alert_id'))
    
    async def send_alert(self, event): 
        """
        Called by the channel layer when a new alert is broadcast.
        Forwards it to this specific websocket client.
        This method name must match what we use in group_send().
        """

        await self.send(text_data=json.dumps(event['paylaod']))
    
    # ---------------------Helpers---------------------------------

    def _get_token_from_query(self): 
        """Extract token from Websocket URL query string."""
        query_string = self.scope.get('query_string', 'b').decode()
        for param in query_string.split('&'): 
            if param.startswith('token='): 
                return param.split('=')[1]
            return None
    
    @database_sync_to_async
    def get_user_from_token(self, token): 
        """Validate JWT token and return the user."""
        try: 
            validated  =AccessToken(token)
            return User.objects.selected_related('role').get(
                id=validated['user_id']
            )
        except Exception: 
            return None
    
    @database_sync_to_async
    def get_unressolved_alerts(self): 
        """Fetch unresolved alerts for this user's location"""
        from .models import Alert 
        queryset = Alert.objects.filter(is_resolved=False)

        if not (self.user.role and self.user.role.name == 'Admin'): 
            queryset = queryset.filter(location=self.user.location)
        
        return list(queryset.values(
            'id', 'type', 'message', 'entity_type', 'entity_id', 'created_at'
        ).order_by('-created_at')[:20])
    
    @database_sync_to_async
    def resolve_alert(self, alert_id): 
        """Mark an alert as resolved """
        from .models import Alert
        from django.utils import timezone
        Alert.objects.filter(id=alert_id).update(
            is_resolved=True, 
            resolved_by=self.user, 
            resolved_at=timezone.now()
        )
