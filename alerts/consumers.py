from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Notification

class NotificationConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        user = self.scope['user']
        if not user.is_authenticated:
            await self.close()
            return
        
        self.group_name = f'notifications_{user.id}'
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

        count = await self._unread_count(user)
        await self.send_json({'type':'unread_count', 'count':count})
    
    async def disconnect(self, code):
        if hasattr(self, 'group_name'):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def send_notification(self, event):
        await self.send_json({
            'type' : 'notification',
            'id' : event['id'],
            'title' : event['title'],
            'body' : event['body'],
        })
    
    async def receive_json(self, content):
        if content.get('type') == 'mark_read':
            nid = content.get('id')
            if nid:
                await self._mark_read(self.scope['user'], nid)

    @database_sync_to_async
    def _unread_count(self, user):
        return Notification.objects.filter(user=user, is_read=False).count()
    
    @database_sync_to_async
    def _mark_read(self, user, notification_id):
        Notification.objects.filter(pk=notification_id, user=user).update(is_read=True)