import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from auctions.models import Notification

User = get_user_model()


class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        """Handle WebSocket connection"""
        self.user = self.scope["user"]

        if self.user.is_anonymous:
            await self.close()
            return

        # Join user-specific notification group
        self.group_name = f"notifications_{self.user.id}"
        await self.channel_layer.group_add(self.group_name, self.channel_name)

        await self.accept()

        # Send unread notifications count on connect
        unread_count = await self.get_unread_count()
        await self.send(
            text_data=json.dumps({"type": "unread_count", "count": unread_count})
        )

    async def disconnect(self, close_code):
        """Handle WebSocket disconnection"""
        if hasattr(self, "group_name"):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        """Handle messages from WebSocket"""
        try:
            data = json.loads(text_data)
            message_type = data.get("type")

            if message_type == "mark_as_read":
                notification_id = data.get("notification_id")
                if notification_id:
                    await self.mark_notification_as_read(notification_id)

            elif message_type == "get_notifications":
                notifications = await self.get_user_notifications()
                await self.send(
                    text_data=json.dumps(
                        {"type": "notifications_list", "notifications": notifications}
                    )
                )

            elif message_type == "mark_all_as_read":
                await self.mark_all_notifications_as_read()
                notifications = await self.get_user_notifications()
                await self.send(
                    text_data=json.dumps(
                        {"type": "notifications_list", "notifications": notifications}
                    )
                )

        except json.JSONDecodeError:
            await self.send(
                text_data=json.dumps({"type": "error", "message": "Invalid JSON"})
            )

    async def notification_message(self, event):
        """Handle notification messages from group"""
        await self.send(
            text_data=json.dumps(
                {"type": "new_notification", "notification": event["notification"]}
            )
        )

    @database_sync_to_async
    def get_unread_count(self):
        """Get count of unread notifications for user"""
        return Notification.objects.filter(user=self.user, is_read=False).count()

    @database_sync_to_async
    def mark_notification_as_read(self, notification_id):
        """Mark a notification as read"""
        try:
            notification = Notification.objects.get(id=notification_id, user=self.user)
            notification.is_read = True
            notification.save()
            return True
        except Notification.DoesNotExist:
            return False

    @database_sync_to_async
    def get_user_notifications(self, limit=20):
        """Get user's recent notifications"""
        notifications = Notification.objects.filter(user=self.user).order_by(
            "-created_at"
        )[:limit]

        return [
            {
                "id": n.id,
                "title": n.title,
                "message": n.message,
                "notification_type": n.notification_type,
                "is_read": n.is_read,
                "created_at": n.created_at.isoformat(),
                "listing_id": n.listing.id if n.listing else None,
            }
            for n in notifications
        ]

    @database_sync_to_async
    def mark_all_notifications_as_read(self):
        """Mark all notifications as read for the user"""
        Notification.objects.filter(user=self.user, is_read=False).update(is_read=True)
