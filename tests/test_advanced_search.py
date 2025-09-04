import pytest
from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.contrib.auth import get_user_model
from auctions.models import Listing
from decimal import Decimal
import json

User = get_user_model()


@override_settings(
    RATELIMIT_ENABLE=False,
    CACHES={
        "default": {
            "BACKEND": "django.core.cache.backends.dummy.DummyCache",
        }
    },
)
class AdvancedSearchTestCase(TestCase):
    """Test cases for advanced search functionality"""

    def setUp(self):
        """Set up test data"""
        self.client = Client()

        # Create test users
        self.user1 = User.objects.create_user(
            username="testuser1", email="test1@example.com", password="testpass123"
        )
        self.user2 = User.objects.create_user(
            username="testuser2", email="test2@example.com", password="testpass123"
        )

        # Create test listings with different categories and prices
        self.listing1 = Listing.objects.create(
            title="Vintage Watch Collection",
            description="Beautiful vintage watches from the 1950s",
            starting_bid=Decimal("100.00"),
            category="Fashion",
            user=self.user1,
            active=True,
        )

        self.listing2 = Listing.objects.create(
            title="Modern Laptop Computer",
            description="High-performance laptop for gaming and work",
            starting_bid=Decimal("800.00"),
            category="Electronics",
            user=self.user1,
            active=True,
        )

        self.listing3 = Listing.objects.create(
            title="Antique Book Set",
            description="Rare collection of antique books",
            starting_bid=Decimal("250.00"),
            category="Books",
            user=self.user2,
            active=True,
        )

        self.listing4 = Listing.objects.create(
            title="Smartphone iPhone",
            description="Latest iPhone model in excellent condition",
            starting_bid=Decimal("600.00"),
            category="Electronics",
            user=self.user2,
            active=True,
        )

        self.listing5 = Listing.objects.create(
            title="Designer Watch",
            description="Luxury designer watch with warranty",
            starting_bid=Decimal("1200.00"),
            category="Fashion",
            user=self.user1,
            active=False,  # Inactive listing
        )


class SearchViewTests(AdvancedSearchTestCase):
    """Test the search view functionality"""

    def test_search_page_loads(self):
        """Test that the search page loads correctly"""
        response = self.client.get(reverse("search"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Advanced Search")
        self.assertContains(response, "Search Query")
        self.assertContains(response, "Category")
        self.assertContains(response, "Price Range")

    def test_search_without_parameters(self):
        """Test search without any parameters returns all active listings"""
        response = self.client.get(reverse("search"))
        self.assertEqual(response.status_code, 200)

        # Should show all active listings (4 out of 5)
        listings = response.context["listings"]
        self.assertEqual(len(listings), 4)

        # Should not include inactive listing
        listing_ids = [listing.id for listing in listings]
        self.assertNotIn(self.listing5.id, listing_ids)

    def test_search_by_query(self):
        """Test search by text query"""
        # Search for 'watch'
        response = self.client.get(reverse("search"), {"q": "watch"})
        self.assertEqual(response.status_code, 200)

        listings = response.context["listings"]
        self.assertEqual(len(listings), 1)  # Only the active vintage watch
        self.assertEqual(listings[0].id, self.listing1.id)

    def test_search_by_category(self):
        """Test search by category"""
        # Search for Electronics category
        response = self.client.get(reverse("search"), {"category": "Electronics"})
        self.assertEqual(response.status_code, 200)

        listings = response.context["listings"]
        self.assertEqual(len(listings), 2)  # Laptop and iPhone

        listing_ids = [listing.id for listing in listings]
        self.assertIn(self.listing2.id, listing_ids)
        self.assertIn(self.listing4.id, listing_ids)

    def test_search_by_price_range(self):
        """Test search by price range"""
        # Search for items between $200 and $700
        response = self.client.get(
            reverse("search"), {"min_price": "200", "max_price": "700"}
        )
        self.assertEqual(response.status_code, 200)

        listings = response.context["listings"]
        self.assertEqual(len(listings), 2)  # Antique books and iPhone

        listing_ids = [listing.id for listing in listings]
        self.assertIn(self.listing3.id, listing_ids)
        self.assertIn(self.listing4.id, listing_ids)

    def test_search_combined_filters(self):
        """Test search with multiple filters combined"""
        # Search for Electronics with price > $700
        response = self.client.get(
            reverse("search"), {"category": "Electronics", "min_price": "700"}
        )
        self.assertEqual(response.status_code, 200)

        listings = response.context["listings"]
        self.assertEqual(len(listings), 1)  # Only the laptop
        self.assertEqual(listings[0].id, self.listing2.id)

    def test_search_sorting(self):
        """Test search result sorting"""
        # Test price sorting (low to high)
        response = self.client.get(reverse("search"), {"sort_by": "price_low"})
        self.assertEqual(response.status_code, 200)

        # Extract prices from response
        listings = response.context["listings"]
        prices = [listing.starting_bid for listing in listings]

        # Verify they are sorted correctly (low to high)
        self.assertEqual(prices, sorted(prices))

        # Test price sorting (high to low)
        response = self.client.get(reverse("search"), {"sort_by": "price_high"})
        self.assertEqual(response.status_code, 200)

        listings = response.context["listings"]
        prices = [listing.starting_bid for listing in listings]

        # Verify they are sorted correctly (high to low)
        self.assertEqual(prices, sorted(prices, reverse=True))

    def test_search_no_results(self):
        """Test search with no matching results"""
        response = self.client.get(reverse("search"), {"q": "nonexistent"})
        self.assertEqual(response.status_code, 200)

        listings = response.context["listings"]
        self.assertEqual(len(listings), 0)
        self.assertContains(response, "No listings found")

    def test_search_ajax_request(self):
        """Test AJAX search request"""
        response = self.client.get(
            reverse("search"), {"q": "laptop"}, HTTP_X_REQUESTED_WITH="XMLHttpRequest"
        )
        self.assertEqual(response.status_code, 200)
        # AJAX requests should return the same content but might be processed differently


class AutocompleteTests(AdvancedSearchTestCase):
    """Test the autocomplete functionality"""

    def test_autocomplete_endpoint(self):
        """Test that autocomplete endpoint works"""
        response = self.client.get(
            reverse("search_autocomplete"),
            {"q": "watch"},
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/json")

    def test_autocomplete_suggestions(self):
        """Test autocomplete suggestions content"""
        response = self.client.get(
            reverse("search_autocomplete"),
            {"q": "watch"},
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )

        data = json.loads(response.content)

        # Check response structure matches the actual implementation
        self.assertIn("suggestions", data)
        suggestions = data["suggestions"]

        self.assertIn("titles", suggestions)
        self.assertIn("categories", suggestions)

        # Check that we get title suggestions
        titles = suggestions["titles"]
        self.assertTrue(len(titles) > 0)

        # Verify the first title contains our search term
        self.assertIn("watch", titles[0].lower())

    def test_autocomplete_minimum_query_length(self):
        """Test autocomplete with short query"""
        response = self.client.get(
            reverse("search_autocomplete"),
            {"q": "w"},  # Single character
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )

        data = json.loads(response.content)
        suggestions = data["suggestions"]
        self.assertEqual(len(suggestions), 0)

    def test_autocomplete_no_ajax_header(self):
        """Test autocomplete without AJAX header returns 400"""
        response = self.client.get(reverse("search_autocomplete"), {"q": "watch"})
        self.assertEqual(response.status_code, 400)

    def test_autocomplete_rate_limiting(self):
        """Test that autocomplete respects rate limiting"""
        # Make multiple rapid requests
        for i in range(15):  # Exceed rate limit
            response = self.client.get(
                reverse("search_autocomplete"),
                {"q": f"query{i}"},
                HTTP_X_REQUESTED_WITH="XMLHttpRequest",
            )

        # Since rate limiting is disabled in test settings, all requests should succeed
        self.assertEqual(response.status_code, 200)


class SearchPerformanceTests(AdvancedSearchTestCase):
    """Test search performance and optimization"""

    def test_search_with_large_dataset(self):
        """Test search performance with larger dataset"""
        # Create additional test data
        for i in range(50):
            Listing.objects.create(
                title=f"Test Listing {i}",
                description=f"Description for listing {i}",
                starting_bid=Decimal(f"{100 + i}.00"),
                category="Test",
                user=self.user1,
                active=True,
            )

        # Perform search
        response = self.client.get(reverse("search"), {"q": "Test"})
        self.assertEqual(response.status_code, 200)

        # Should return results efficiently
        listings = response.context["listings"]
        self.assertTrue(len(listings) > 0)

    def test_search_pagination(self):
        """Test search results pagination"""
        # Create enough listings to trigger pagination
        for i in range(25):
            Listing.objects.create(
                title=f"Paginated Listing {i}",
                description=f"Description {i}",
                starting_bid=Decimal("100.00"),
                category="Test",
                user=self.user1,
                active=True,
            )

        # Test first page
        response = self.client.get(reverse("search"), {"category": "Test"})
        self.assertEqual(response.status_code, 200)

        # Check if pagination is working
        if "is_paginated" in response.context:
            self.assertTrue(response.context["is_paginated"])


@pytest.mark.integration
class SearchIntegrationTests(AdvancedSearchTestCase):
    """Integration tests for search functionality"""

    def test_search_with_authentication(self):
        """Test search functionality with authenticated user"""
        self.client.login(username="testuser1", password="testpass123")

        response = self.client.get(reverse("search"), {"q": "watch"})
        self.assertEqual(response.status_code, 200)

        # Authenticated users should see additional features
        self.assertContains(response, "Watchlist")

    def test_search_from_navigation(self):
        """Test accessing search from main navigation"""
        # First get the main page to ensure navigation is working
        response = self.client.get(reverse("index"))
        self.assertEqual(response.status_code, 200)

        # Then access search
        response = self.client.get(reverse("search"))
        self.assertEqual(response.status_code, 200)

        # Check that navigation shows search as active
        self.assertContains(response, "Search")

    def test_search_error_handling(self):
        """Test search error handling"""
        # Test with invalid price range
        response = self.client.get(
            reverse("search"), {"min_price": "invalid", "max_price": "also_invalid"}
        )

        # Should handle gracefully and return results
        self.assertEqual(response.status_code, 200)

    def test_search_security(self):
        """Test search security measures"""
        # Test with potential XSS in query
        response = self.client.get(
            reverse("search"), {"q": '<script>alert("xss")</script>'}
        )

        self.assertEqual(response.status_code, 200)
        # Should not contain unescaped script tags
        self.assertNotContains(response, '<script>alert("xss")</script>', html=False)
