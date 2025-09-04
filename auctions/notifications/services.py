from django.contrib.auth import get_user_model
from auctions.models import Notification
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

User = get_user_model()


class NotificationService:
    """Service for creating and managing notifications"""

    @staticmethod
    def create_bid_notification(listing, bid, bidder):
        """Create notification when a new bid is placed"""
        # Notify listing owner
        if listing.user != bidder:
            notification = Notification.objects.create(
                user=listing.user,
                notification_type="bid",
                title=f"New bid on {listing.title}",
                message=f"{bidder.username} placed a bid of ${bid.amount} on {listing.title}.",
                listing=listing,
            )
            NotificationService.send_real_time_notification(notification)
            return notification
        return None

    @staticmethod
    def create_outbid_notification(previous_bidder, listing, new_bid):
        """Create notification when a user is outbid"""
        if previous_bidder and previous_bidder != new_bid.user:
            notification = Notification.objects.create(
                user=previous_bidder,
                notification_type="outbid",
                title=f"You have been outbid on {listing.title}",
                message=f"You have been outbid on {listing.title}. Someone placed a higher bid of ${new_bid.amount}.",
                listing=listing,
            )
            NotificationService.send_real_time_notification(notification)
            return notification
        return None

    @staticmethod
    def create_auction_ending_notification(user, listing, hours_remaining=24):
        """Create notification when auction is ending soon"""
        notification = Notification.objects.create(
            user=user,
            notification_type="auction_ending",
            title=f"Auction ending soon: {listing.title}",
            message=f"The auction for {listing.title} is ending soon.",
            listing=listing,
        )
        NotificationService.send_real_time_notification(notification)
        return notification

    @staticmethod
    def send_real_time_notification(notification):
        """Send real-time notification via WebSocket"""
        try:
            channel_layer = get_channel_layer()
            if channel_layer:
                async_to_sync(channel_layer.group_send)(
                    f"notifications_{notification.user.id}",
                    {
                        "type": "notification_message",
                        "notification": {
                            "id": notification.id,
                            "title": notification.title,
                            "message": notification.message,
                            "type": notification.notification_type,
                            "created_at": notification.created_at.isoformat(),
                            "listing_id": (
                                notification.listing.id
                                if notification.listing
                                else None
                            ),
                        },
                    },
                )
        except Exception as e:
            # Log error but don't fail the notification creation
            print(f"Error sending real-time notification: {e}")

    @staticmethod
    def mark_all_as_read(user):
        """Mark all notifications as read for a user"""
        return Notification.objects.filter(user=user, is_read=False).update(
            is_read=True
        )

    @staticmethod
    def get_user_notifications(user, limit=50):
        """Get notifications for a user with pagination"""
        return Notification.objects.filter(user=user).order_by("-created_at")[:limit]
