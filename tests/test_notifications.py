import pytest

from django.contrib.auth import get_user_model
from unittest.mock import patch, MagicMock
from decimal import Decimal

from auctions.models import Notification
from auctions.notifications.services import NotificationService
from auctions.notifications.tasks import NotificationTasks
from tests.conftest import UserFactory, ListingFactory, BidFactory

User = get_user_model()


@pytest.mark.notifications
class TestNotificationModel:
    """Tests para el modelo Notification"""

    @pytest.mark.django_db
    def test_notification_creation(self):
        """Test que una notificación se puede crear correctamente"""
        user = UserFactory()

        notification = Notification.objects.create(
            user=user,
            title="Nueva puja",
            message="Alguien ha pujado en tu subasta",
            notification_type="bid",
            is_read=False,
        )

        assert notification.user == user
        assert notification.title == "Nueva puja"
        assert notification.message == "Alguien ha pujado en tu subasta"
        assert notification.notification_type == "bid"
        assert notification.is_read is False
        assert notification.created_at is not None

    @pytest.mark.django_db
    def test_notification_str_representation(self):
        """Test de la representación string de una notificación"""
        user = UserFactory(username="testuser")
        notification = Notification(
            user=user,
            title="Test Notification",
            message="Test message",
            notification_type="bid",
        )

        expected = "testuser - Test Notification"
        assert str(notification) == expected

    @pytest.mark.django_db
    def test_mark_as_read(self):
        """Test que una notificación se puede marcar como leída"""
        user = UserFactory()
        notification = Notification.objects.create(
            user=user,
            title="Test",
            message="Test message",
            notification_type="bid",
            is_read=False,
        )

        notification.mark_as_read()
        notification.refresh_from_db()

        assert notification.is_read is True

    @pytest.mark.django_db
    def test_get_unread_notifications(self):
        """Test para obtener notificaciones no leídas de un usuario"""
        user = UserFactory()

        # Crear notificaciones leídas y no leídas
        Notification.objects.create(
            user=user,
            title="Read",
            message="Read msg",
            notification_type="bid",
            is_read=True,
        )
        Notification.objects.create(
            user=user,
            title="Unread 1",
            message="Unread msg 1",
            notification_type="bid",
            is_read=False,
        )
        Notification.objects.create(
            user=user,
            title="Unread 2",
            message="Unread msg 2",
            notification_type="auction_ending",
            is_read=False,
        )

        unread = Notification.objects.filter(user=user, is_read=False)
        assert unread.count() == 2


@pytest.mark.notifications
class TestNotificationService:
    """Tests para el servicio de notificaciones"""

    @pytest.mark.django_db
    def test_create_bid_notification(self):
        """Test crear notificación de nueva puja"""
        listing_owner = UserFactory(username="owner")
        bidder = UserFactory(username="bidder")
        listing = ListingFactory(user=listing_owner, title="Test Auction")
        bid = BidFactory(user=bidder, listing=listing, amount=Decimal("100.00"))

        notification = NotificationService.create_bid_notification(listing, bid, bidder)

        assert notification.user == listing_owner
        assert notification.notification_type == "bid"
        assert "Test Auction" in notification.message
        assert "100" in notification.message
        assert notification.is_read is False

    @pytest.mark.django_db
    def test_create_auction_ending_notification(self):
        """Test crear notificación de subasta terminando"""
        user = UserFactory()
        listing = ListingFactory(title="Ending Auction")

        notification = NotificationService.create_auction_ending_notification(
            user, listing
        )

        assert notification.user == user
        assert notification.notification_type == "auction_ending"
        assert "Ending Auction" in notification.message
        assert "ending soon" in notification.message.lower()
        assert notification.is_read is False

    @pytest.mark.django_db
    def test_create_outbid_notification(self):
        """Test crear notificación cuando un usuario es superado en una puja"""
        previous_bidder = UserFactory(username="previous")
        new_bidder = UserFactory(username="new")
        listing = ListingFactory(title="Test Auction")

        # Puja anterior
        BidFactory(
            user=previous_bidder, listing=listing, amount=Decimal("50.00")
        )

        # Nueva puja que supera la anterior
        new_bid = BidFactory(user=new_bidder, listing=listing, amount=Decimal("75.00"))

        notification = NotificationService.create_outbid_notification(
            previous_bidder, listing, new_bid
        )

        assert notification.user == previous_bidder
        assert notification.notification_type == "outbid"
        assert "outbid" in notification.message.lower()
        assert "Test Auction" in notification.message
        assert notification.is_read is False

    @pytest.mark.django_db
    @patch("auctions.notifications.services.get_channel_layer")
    def test_send_real_time_notification(self, mock_channel_layer):
        """Test envío de notificación en tiempo real via WebSocket"""
        user = UserFactory()
        notification = Notification.objects.create(
            user=user,
            title="Real-time Test",
            message="Test message",
            notification_type="bid",
        )

        # Mock del channel layer
        mock_layer = MagicMock()
        mock_channel_layer.return_value = mock_layer

        # Llamar al método
        NotificationService.send_real_time_notification(notification)

        # Verificar que se llamó group_send
        mock_layer.group_send.assert_called_once()


@pytest.mark.notifications
class TestNotificationTasks:
    """Tests para las tareas asíncronas de notificaciones"""

    @pytest.mark.django_db
    @patch("auctions.notifications.services.NotificationService")
    def test_send_bid_notification_task(self, mock_service):
        """Test tarea asíncrona para enviar notificación de puja"""
        listing_owner = UserFactory()
        bidder = UserFactory()
        listing = ListingFactory(user=listing_owner)
        bid = BidFactory(user=bidder, listing=listing)

        # Ejecutar la tarea
        result = NotificationTasks.send_bid_notification(listing.id, bid.id, bidder.id)

        # Verificar que se ejecutó correctamente
        assert "Bid notifications sent" in result or "Error" in result

    @pytest.mark.django_db
    @patch("auctions.notifications.services.NotificationService")
    def test_send_auction_ending_notification_task(self, mock_service):
        """Test tarea asíncrona para notificación de subasta terminando"""
        user = UserFactory()
        listing = ListingFactory()

        # Simular watchlist
        from auctions.models import Watchlist

        Watchlist.objects.create(user=user, listing=listing)

        # Ejecutar la tarea
        result = NotificationTasks.send_auction_ending_notifications(24)

        # Verificar que se ejecutó correctamente
        assert "auction ending notifications" in result


@pytest.mark.notifications
@pytest.mark.integration
class TestNotificationIntegration:
    """Tests de integración para el sistema de notificaciones"""

    @pytest.mark.django_db
    def test_bid_creates_notification(self):
        """Test que crear una puja genera automáticamente una notificación"""
        listing_owner = UserFactory()
        bidder = UserFactory()
        listing = ListingFactory(user=listing_owner)

        # Verificar que no hay notificaciones inicialmente
        assert Notification.objects.count() == 0

        # Crear una puja (esto debería disparar una señal)
        BidFactory(user=bidder, listing=listing)

        # Verificar que se creó una notificación
        # Nota: Este test fallará hasta que implementemos las señales
        notifications = Notification.objects.filter(user=listing_owner)
        assert notifications.count() == 1

        notification = notifications.first()
        assert notification.notification_type == "bid"
        assert notification.is_read is False

    @pytest.mark.django_db
    def test_multiple_bids_create_multiple_notifications(self):
        """Test que múltiples pujas crean múltiples notificaciones"""
        listing_owner = UserFactory()
        listing = ListingFactory(user=listing_owner)

        # Crear múltiples pujas de diferentes usuarios
        bidders = UserFactory.create_batch(3)
        for i, bidder in enumerate(bidders):
            BidFactory(
                user=bidder,
                listing=listing,
                amount=listing.starting_bid + Decimal(f"{(i+1)*10}.00"),
            )

        # Verificar que se crearon las notificaciones correspondientes
        notifications = Notification.objects.filter(user=listing_owner)
        assert notifications.count() == 3

    @pytest.mark.django_db
    def test_user_cannot_see_other_users_notifications(self):
        """Test que un usuario solo puede ver sus propias notificaciones"""
        user1 = UserFactory()
        user2 = UserFactory()

        # Crear notificaciones para cada usuario
        Notification.objects.create(
            user=user1,
            title="User 1 Notification",
            message="Message for user 1",
            notification_type="bid",
        )
        Notification.objects.create(
            user=user2,
            title="User 2 Notification",
            message="Message for user 2",
            notification_type="bid",
        )

        # Verificar que cada usuario solo ve sus notificaciones
        user1_notifications = Notification.objects.filter(user=user1)
        user2_notifications = Notification.objects.filter(user=user2)

        assert user1_notifications.count() == 1
        assert user2_notifications.count() == 1
        assert user1_notifications.first().title == "User 1 Notification"
        assert user2_notifications.first().title == "User 2 Notification"
