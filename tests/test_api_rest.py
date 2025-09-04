from decimal import Decimal
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from auctions.models import Listing, Bid, Comment, Watchlist

User = get_user_model()


class APIAuthenticationTestCase(APITestCase):
    """
    Test JWT authentication for API endpoints.
    """

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.client = APIClient()

    def test_token_obtain_pair(self):
        """Test JWT token generation."""
        url = reverse("token_obtain_pair")
        data = {"username": "testuser", "password": "testpass123"}
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)
        self.assertIn("user", response.data)
        self.assertEqual(response.data["user"]["username"], "testuser")

    def test_token_obtain_pair_invalid_credentials(self):
        """Test JWT token generation with invalid credentials."""
        url = reverse("token_obtain_pair")
        data = {"username": "testuser", "password": "wrongpassword"}
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_token_refresh(self):
        """Test JWT token refresh."""
        refresh = RefreshToken.for_user(self.user)
        url = reverse("token_refresh")
        data = {"refresh": str(refresh)}

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)

    def test_protected_endpoint_without_token(self):
        """Test accessing protected endpoint without token."""
        url = "/api/v1/users/me/"
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_protected_endpoint_with_token(self):
        """Test accessing protected endpoint with valid token."""
        refresh = RefreshToken.for_user(self.user)
        access_token = refresh.access_token

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
        url = "/api/v1/users/me/"
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], "testuser")


class UserAPITestCase(APITestCase):
    """
    Test User API endpoints.
    """

    def setUp(self):
        self.user1 = User.objects.create_user(
            username="user1", email="user1@example.com", password="testpass123"
        )
        self.user2 = User.objects.create_user(
            username="user2", email="user2@example.com", password="testpass123"
        )
        self.client = APIClient()

        # Authenticate user1
        refresh = RefreshToken.for_user(self.user1)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

    def test_list_users(self):
        """Test listing users."""
        url = "/api/v1/users/"
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 2)

    def test_get_user_detail(self):
        """Test getting user detail."""
        url = f"/api/v1/users/{self.user2.id}/"
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], "user2")
        self.assertNotIn("email", response.data)  # Should use public serializer

    def test_get_current_user(self):
        """Test getting current user info."""
        url = "/api/v1/users/me/"
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], "user1")
        self.assertIn("email", response.data)  # Should include private info

    def test_search_users(self):
        """Test searching users."""
        url = "/api/v1/users/?search=user1"
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["username"], "user1")


class ListingAPITestCase(APITestCase):
    """
    Test Listing API endpoints.
    """

    def setUp(self):
        self.user1 = User.objects.create_user(
            username="user1", email="user1@example.com", password="testpass123"
        )
        self.user2 = User.objects.create_user(
            username="user2", email="user2@example.com", password="testpass123"
        )

        self.listing1 = Listing.objects.create(
            title="iPhone 12",
            description="Great phone",
            starting_bid=Decimal("500.00"),
            user=self.user1,
            category="Electronics",
        )

        self.listing2 = Listing.objects.create(
            title="Samsung Galaxy",
            description="Android phone",
            starting_bid=Decimal("400.00"),
            user=self.user2,
            category="Electronics",
            active=False,
        )

        self.client = APIClient()

        # Authenticate user1
        refresh = RefreshToken.for_user(self.user1)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

    def test_list_listings(self):
        """Test listing all listings (only active by default)."""
        url = "/api/v1/listings/"
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)  # Only active listings

    def test_filter_active_listings(self):
        """Test filtering active listings."""
        url = "/api/v1/listings/?active=true"
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["title"], "iPhone 12")

    def test_search_listings(self):
        """Test searching listings."""
        url = "/api/v1/listings/?search=iPhone"
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["title"], "iPhone 12")

    def test_filter_by_price_range(self):
        """Test filtering listings by price range."""
        url = "/api/v1/listings/?min_price=450&max_price=550"
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["title"], "iPhone 12")

    def test_create_listing(self):
        """Test creating a new listing."""
        url = "/api/v1/listings/"
        data = {
            "title": "MacBook Pro",
            "description": "Laptop for sale",
            "starting_bid": "1000.00",
            "category": "Electronics",
        }
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["title"], "MacBook Pro")
        self.assertEqual(response.data["user"]["username"], "user1")

    def test_update_own_listing(self):
        """Test updating own listing."""
        url = f"/api/v1/listings/{self.listing1.id}/"
        data = {
            "title": "iPhone 12 Pro",
            "description": "Updated description",
            "starting_bid": "550.00",
            "category": "Electronics",
        }
        response = self.client.put(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "iPhone 12 Pro")

    def test_update_other_user_listing_forbidden(self):
        """Test updating another user's listing should be forbidden."""
        url = f"/api/v1/listings/{self.listing2.id}/"
        data = {
            "title": "Updated title",
            "description": "Updated description",
            "starting_bid": "450.00",
            "category": "Electronics",
        }
        response = self.client.put(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_own_listing(self):
        """Test deleting own listing."""
        url = f"/api/v1/listings/{self.listing1.id}/"
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Listing.objects.filter(id=self.listing1.id).exists())

    def test_delete_other_user_listing_forbidden(self):
        """Test deleting another user's listing should be forbidden."""
        url = f"/api/v1/listings/{self.listing2.id}/"
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_place_bid_on_listing(self):
        """Test placing a bid on a listing."""
        # Make listing2 active so we can bid on it
        self.listing2.active = True
        self.listing2.save()

        url = f"/api/v1/listings/{self.listing2.id}/bid/"
        data = {"amount": "450.00"}  # Higher than listing2's starting bid of 400
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Decimal(response.data["amount"]), Decimal("450.00"))

    def test_place_invalid_bid(self):
        """Test placing an invalid bid (too low)."""
        url = f"/api/v1/listings/{self.listing1.id}/bid/"
        data = {"amount": "400.00"}  # Lower than starting bid
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_close_own_listing(self):
        """Test closing own listing."""
        url = f"/api/v1/listings/{self.listing1.id}/close/"
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.listing1.refresh_from_db()
        self.assertFalse(self.listing1.active)

    def test_close_other_user_listing_forbidden(self):
        """Test closing another user's listing should be forbidden."""
        url = f"/api/v1/listings/{self.listing2.id}/close/"
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # def test_get_listing_stats(self):
    #     """Test getting listing statistics."""
    #     # Create some bids and comments
    #     Bid.objects.create(user=self.user2, listing=self.listing1, amount=Decimal('520.00'))
    #     Comment.objects.create(user=self.user2, listing=self.listing1, text='Great item!')
    #
    #     url = f'/api/v1/listings/{self.listing1.id}/stats/'
    #     response = self.client.get(url)
    #
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     self.assertEqual(response.data['bid_count'], 1)
    #     self.assertEqual(response.data['comment_count'], 1)
    #     self.assertEqual(Decimal(response.data['highest_bid']), Decimal('520.00'))


class BidAPITestCase(APITestCase):
    """
    Test Bid API endpoints.
    """

    def setUp(self):
        self.user1 = User.objects.create_user(
            username="user1", email="user1@example.com", password="testpass123"
        )
        self.user2 = User.objects.create_user(
            username="user2", email="user2@example.com", password="testpass123"
        )

        self.listing = Listing.objects.create(
            title="iPhone 12",
            description="Great phone",
            starting_bid=Decimal("500.00"),
            user=self.user1,
            category="Electronics",
        )

        self.bid = Bid.objects.create(
            user=self.user2, listing=self.listing, amount=Decimal("550.00")
        )

        self.client = APIClient()

        # Authenticate user2
        refresh = RefreshToken.for_user(self.user2)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

    def test_list_user_bids(self):
        """Test listing user's bids."""
        url = "/api/v1/bids/"
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(
            Decimal(response.data["results"][0]["amount"]), Decimal("550.00")
        )

    def test_create_bid(self):
        """Test creating a new bid."""
        url = "/api/v1/bids/"
        data = {"listing": self.listing.id, "amount": "600.00"}
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Decimal(response.data["amount"]), Decimal("600.00"))

    def test_filter_bids_by_listing(self):
        """Test filtering bids by listing."""
        url = f"/api/v1/bids/?listing={self.listing.id}"
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)


class WatchlistAPITestCase(APITestCase):
    """
    Test Watchlist API endpoints.
    """

    def setUp(self):
        self.user1 = User.objects.create_user(
            username="user1", email="user1@example.com", password="testpass123"
        )
        self.user2 = User.objects.create_user(
            username="user2", email="user2@example.com", password="testpass123"
        )

        self.listing = Listing.objects.create(
            title="iPhone 12",
            description="Great phone",
            starting_bid=Decimal("500.00"),
            user=self.user2,
            category="Electronics",
        )

        self.watchlist_item = Watchlist.objects.create(
            user=self.user1, listing=self.listing
        )

        self.client = APIClient()

        # Authenticate user1
        refresh = RefreshToken.for_user(self.user1)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

    def test_list_watchlist(self):
        """Test listing user's watchlist."""
        url = "/api/v1/watchlist/"
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["listing"]["title"], "iPhone 12")

    def test_add_to_watchlist(self):
        """Test adding item to watchlist."""
        # Create another listing
        listing2 = Listing.objects.create(
            title="Samsung Galaxy",
            description="Android phone",
            starting_bid=Decimal("400.00"),
            user=self.user2,
            category="Electronics",
        )

        url = "/api/v1/watchlist/"
        data = {"listing_id": listing2.id}
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["listing"]["title"], "Samsung Galaxy")

    def test_remove_from_watchlist(self):
        """Test removing item from watchlist."""
        url = f"/api/v1/watchlist/{self.watchlist_item.id}/"
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Watchlist.objects.filter(id=self.watchlist_item.id).exists())

    def test_toggle_watchlist(self):
        """Test toggling watchlist item."""
        # Create another listing
        listing2 = Listing.objects.create(
            title="Samsung Galaxy",
            description="Android phone",
            starting_bid=Decimal("400.00"),
            user=self.user2,
            category="Electronics",
        )

        url = "/api/v1/watchlist/toggle/"
        data = {"listing_id": listing2.id}

        # First toggle - should add to watchlist
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data["watching"])

        # Second toggle - should remove from watchlist
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data["watching"])


class CommentAPITestCase(APITestCase):
    """
    Test Comment API endpoints.
    """

    def setUp(self):
        self.user1 = User.objects.create_user(
            username="user1", email="user1@example.com", password="testpass123"
        )
        self.user2 = User.objects.create_user(
            username="user2", email="user2@example.com", password="testpass123"
        )

        self.listing = Listing.objects.create(
            title="iPhone 12",
            description="Great phone",
            starting_bid=Decimal("500.00"),
            user=self.user1,
            category="Electronics",
        )

        self.comment = Comment.objects.create(
            user=self.user2, listing=self.listing, text="Great item!"
        )

        self.client = APIClient()

        # Authenticate user2
        refresh = RefreshToken.for_user(self.user2)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

    def test_list_comments(self):
        """Test listing comments."""
        url = "/api/v1/comments/"
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["text"], "Great item!")

    def test_create_comment(self):
        """Test creating a new comment."""
        url = "/api/v1/comments/"
        data = {"listing": self.listing.id, "text": "Another great comment!"}
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["text"], "Another great comment!")

    def test_update_own_comment(self):
        """Test updating own comment."""
        url = f"/api/v1/comments/{self.comment.id}/"
        data = {"listing": self.listing.id, "text": "Updated comment content"}
        response = self.client.put(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["text"], "Updated comment content")

    def test_delete_own_comment(self):
        """Test deleting own comment."""
        url = f"/api/v1/comments/{self.comment.id}/"
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Comment.objects.filter(id=self.comment.id).exists())

    def test_filter_comments_by_listing(self):
        """Test filtering comments by listing."""
        url = f"/api/v1/comments/?listing={self.listing.id}"
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)


class APIPaginationTestCase(APITestCase):
    """
    Test API pagination.
    """

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

        # Create multiple listings for pagination testing
        for i in range(25):
            Listing.objects.create(
                title=f"Listing {i}",
                description=f"Description {i}",
                starting_bid=Decimal("100.00"),
                user=self.user,
                category="Electronics",
            )

        self.client = APIClient()

        # Authenticate user
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

    def test_pagination_first_page(self):
        """Test first page of paginated results."""
        url = "/api/v1/listings/"
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 20)  # Default page size
        self.assertIsNotNone(response.data["next"])
        self.assertIsNone(response.data["previous"])

    def test_pagination_second_page(self):
        """Test second page of paginated results."""
        url = "/api/v1/listings/?page=2"
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 5)  # Remaining items
        self.assertIsNone(response.data["next"])
        self.assertIsNotNone(response.data["previous"])

    def test_custom_page_size(self):
        """Test custom page size."""
        url = "/api/v1/listings/?page_size=10"
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 10)


class APIOrderingTestCase(APITestCase):
    """
    Test API ordering functionality.
    """

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

        # Create listings with different prices
        self.listing1 = Listing.objects.create(
            title="Cheap Item",
            description="Low price",
            starting_bid=Decimal("100.00"),
            user=self.user,
            category="Electronics",
        )

        self.listing2 = Listing.objects.create(
            title="Expensive Item",
            description="High price",
            starting_bid=Decimal("500.00"),
            user=self.user,
            category="Electronics",
        )

        self.client = APIClient()

        # Authenticate user
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

    def test_order_by_price_ascending(self):
        """Test ordering by price ascending."""
        url = "/api/v1/listings/?ordering=starting_bid"
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data["results"]
        self.assertEqual(results[0]["title"], "Cheap Item")
        self.assertEqual(results[1]["title"], "Expensive Item")

    def test_order_by_price_descending(self):
        """Test ordering by price descending."""
        url = "/api/v1/listings/?ordering=-starting_bid"
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data["results"]
        self.assertEqual(results[0]["title"], "Expensive Item")
        self.assertEqual(results[1]["title"], "Cheap Item")

    def test_order_by_title(self):
        """Test ordering by title."""
        url = "/api/v1/listings/?ordering=title"
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data["results"]
        self.assertEqual(results[0]["title"], "Cheap Item")
        self.assertEqual(results[1]["title"], "Expensive Item")
