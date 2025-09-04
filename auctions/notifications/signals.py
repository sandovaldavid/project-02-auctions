from django.db.models.signals import post_save
from django.dispatch import receiver
from auctions.models import Bid
from .services import NotificationService


@receiver(post_save, sender=Bid)
def create_bid_notification(sender, instance, created, **kwargs):
    """Crear notificación cuando se crea una nueva puja"""
    if created:
        # Notificar al dueño de la subasta
        NotificationService.create_bid_notification(
            listing=instance.listing, bid=instance, bidder=instance.user
        )

        # Notificar a pujas anteriores que fueron superadas
        previous_bidders = (
            Bid.objects.filter(listing=instance.listing, amount__lt=instance.amount)
            .exclude(user=instance.user)
            .values_list("user", flat=True)
            .distinct()
        )

        for bidder_id in previous_bidders:
            from django.contrib.auth import get_user_model

            User = get_user_model()
            previous_bidder = User.objects.get(id=bidder_id)
            NotificationService.create_outbid_notification(
                previous_bidder=previous_bidder,
                listing=instance.listing,
                new_bid=instance,
            )
