from celery import shared_task
from django.contrib.auth import get_user_model
from .services import NotificationService
from auctions.models import Listing, Bid
from django.utils import timezone
from datetime import timedelta

User = get_user_model()


class NotificationTasks:
    """Celery tasks for notifications"""

    @staticmethod
    @shared_task
    def send_bid_notification(listing_id, bid_id, bidder_id):
        """Async task to send bid notification"""
        try:
            listing = Listing.objects.get(id=listing_id)
            bid = Bid.objects.get(id=bid_id)
            bidder = User.objects.get(id=bidder_id)

            # Create bid notification
            NotificationService.create_bid_notification(listing, bid, bidder)

            # Check if there was a previous highest bidder to notify about outbid
            previous_bids = (
                Bid.objects.filter(listing=listing, amount__lt=bid.amount)
                .order_by("-amount")
                .first()
            )

            if previous_bids:
                NotificationService.create_outbid_notification(
                    listing, bid, previous_bids.user
                )

            return f"Bid notifications sent for listing {listing_id}"
        except Exception as e:
            return f"Error sending bid notification: {str(e)}"

    @staticmethod
    @shared_task
    def send_auction_ending_notifications(hours_before=24):
        """Async task to send auction ending notifications"""
        try:
            # Find auctions ending in the specified hours
            end_time = timezone.now() + timedelta(hours=hours_before)
            start_time = timezone.now() + timedelta(hours=hours_before - 1)

            ending_listings = Listing.objects.filter(
                active=True, created_at__range=[start_time, end_time]
            )

            notifications_sent = 0
            for listing in ending_listings:
                notifications = NotificationService.create_auction_ending_notification(
                    listing, hours_before
                )
                notifications_sent += len(notifications)

            return f"Sent {notifications_sent} auction ending notifications"
        except Exception as e:
            return f"Error sending auction ending notifications: {str(e)}"

    @staticmethod
    @shared_task
    def cleanup_old_notifications(days_old=30):
        """Async task to cleanup old read notifications"""
        try:
            from .models import Notification

            cutoff_date = timezone.now() - timedelta(days=days_old)

            deleted_count = Notification.objects.filter(
                is_read=True, created_at__lt=cutoff_date
            ).delete()[0]

            return f"Cleaned up {deleted_count} old notifications"
        except Exception as e:
            return f"Error cleaning up notifications: {str(e)}"
