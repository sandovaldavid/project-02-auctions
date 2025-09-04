import pytest
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.conf import settings
from unittest.mock import patch

from tests.conftest import UserFactory, ListingFactory

User = get_user_model()

# Skip tests that require django_ratelimit if not available
try:
    import django_ratelimit  # noqa: F401
    RATELIMIT_AVAILABLE = True
except ImportError:
    RATELIMIT_AVAILABLE = False

skip_if_no_ratelimit = pytest.mark.skipif(
    not RATELIMIT_AVAILABLE, reason="django_ratelimit not available"
)


class RateLimitingTestCase(TestCase):
    """Base test case for rate limiting tests"""

    def setUp(self):
        self.client = Client()
        self.user = UserFactory()
        self.listing = ListingFactory()
        # Clear cache before each test
        cache.clear()

    def tearDown(self):
        # Clear cache after each test
        cache.clear()


@pytest.mark.rate_limiting
@skip_if_no_ratelimit
class TestLoginRateLimit(RateLimitingTestCase):
    """Test rate limiting for login attempts"""

    def test_login_rate_limit_by_ip(self):
        """Test that login attempts are rate limited by IP address"""
        login_url = reverse("login")

        # Make multiple failed login attempts
        for i in range(6):  # Assuming limit is 5 per minute
            response = self.client.post(
                login_url, {"username": "nonexistent", "password": "wrongpassword"}
            )

            if i < 5:
                # First 5 attempts should be allowed
                self.assertNotEqual(response.status_code, 429)
            else:
                # 6th attempt should be rate limited
                self.assertEqual(response.status_code, 429)

    def test_login_rate_limit_by_user(self):
        """Test that login attempts are rate limited by username"""
        login_url = reverse("login")

        # Make multiple failed login attempts for the same user
        for i in range(6):
            response = self.client.post(
                login_url, {"username": self.user.username, "password": "wrongpassword"}
            )

            if i < 5:
                self.assertNotEqual(response.status_code, 429)
            else:
                self.assertEqual(response.status_code, 429)

    def test_successful_login_resets_counter(self):
        """Test that successful login resets the rate limit counter"""
        login_url = reverse("login")

        # Make some failed attempts
        for i in range(3):
            self.client.post(
                login_url, {"username": self.user.username, "password": "wrongpassword"}
            )

        # Successful login should reset counter
        response = self.client.post(
            login_url, {"username": self.user.username, "password": "testpass123"}
        )

        # Should redirect on successful login
        self.assertEqual(response.status_code, 302)

        # Logout and try failed attempts again
        self.client.logout()

        # Should be able to make failed attempts again
        for i in range(3):
            response = self.client.post(
                login_url, {"username": self.user.username, "password": "wrongpassword"}
            )
            self.assertNotEqual(response.status_code, 429)


@pytest.mark.rate_limiting
@skip_if_no_ratelimit
class TestBiddingRateLimit(RateLimitingTestCase):
    """Test rate limiting for bidding actions"""

    def test_bidding_rate_limit_authenticated_user(self):
        """Test that bidding is rate limited for authenticated users"""
        self.client.force_login(self.user)
        bid_url = reverse("bid", args=[self.listing.id])

        # Make multiple bid attempts
        for i in range(11):  # Assuming limit is 10 bids per minute
            response = self.client.post(
                bid_url, {"bid": str(self.listing.starting_bid + i + 1)}
            )

            if i < 10:
                # First 10 bids should be allowed (or fail for business logic reasons)
                self.assertNotEqual(response.status_code, 429)
            else:
                # 11th bid should be rate limited
                self.assertEqual(response.status_code, 429)

    def test_bidding_rate_limit_by_ip(self):
        """Test that bidding is rate limited by IP for anonymous users"""
        bid_url = reverse("bid", args=[self.listing.id])

        # Anonymous users should be redirected to login
        # But rate limiting should still apply to the IP
        for i in range(6):
            response = self.client.post(
                bid_url, {"bid": str(self.listing.starting_bid + i + 1)}
            )

            if i < 5:
                # Should redirect to login (not rate limited)
                self.assertEqual(response.status_code, 302)
            else:
                # Should be rate limited
                self.assertEqual(response.status_code, 429)


@pytest.mark.rate_limiting
@skip_if_no_ratelimit
class TestListingCreationRateLimit(RateLimitingTestCase):
    """Test rate limiting for listing creation"""

    def test_listing_creation_rate_limit(self):
        """Test that listing creation is rate limited"""
        self.client.force_login(self.user)
        create_url = reverse("addAuctions")

        # Make multiple listing creation attempts
        for i in range(4):  # Assuming limit is 3 listings per hour
            response = self.client.post(
                create_url,
                {
                    "title": f"Test Listing {i}",
                    "description": "Test description",
                    "starting_bid": "10.00",
                    "category": "Test Category",
                    "image": "",
                },
            )

            if i < 3:
                # First 3 listings should be allowed
                self.assertIn(response.status_code, [200, 302])  # Success or redirect
            else:
                # 4th listing should be rate limited
                self.assertEqual(response.status_code, 429)


@pytest.mark.rate_limiting
@skip_if_no_ratelimit
class TestCommentRateLimit(RateLimitingTestCase):
    """Test rate limiting for comments"""

    def test_comment_rate_limit(self):
        """Test that commenting is rate limited"""
        self.client.force_login(self.user)
        comment_url = reverse("comment", args=[self.listing.id])

        # Make multiple comment attempts
        for i in range(6):  # Assuming limit is 5 comments per minute
            response = self.client.post(comment_url, {"comment": f"Test comment {i}"})

            if i < 5:
                # First 5 comments should be allowed
                self.assertIn(response.status_code, [200, 302])
            else:
                # 6th comment should be rate limited
                self.assertEqual(response.status_code, 429)


@pytest.mark.rate_limiting
@skip_if_no_ratelimit
class TestAPIRateLimit(RateLimitingTestCase):
    """Test rate limiting for API endpoints"""

    def test_api_rate_limit_anonymous(self):
        """Test API rate limiting for anonymous users"""
        # Use the index page for testing rate limiting
        api_url = reverse("index")

        # Make multiple API requests
        for i in range(101):  # Assuming limit is 100 requests per hour
            response = self.client.get(api_url)

            if i < 100:
                # First 100 requests should be allowed
                self.assertNotEqual(response.status_code, 429)
            else:
                # 101st request should be rate limited
                self.assertEqual(response.status_code, 429)

    def test_api_rate_limit_authenticated(self):
        """Test API rate limiting for authenticated users"""
        self.client.force_login(self.user)
        api_url = reverse("index")

        # Authenticated users should have higher limits
        for i in range(501):  # Assuming limit is 500 requests per hour
            response = self.client.get(api_url)

            if i < 500:
                self.assertNotEqual(response.status_code, 429)
            else:
                self.assertEqual(response.status_code, 429)


@pytest.mark.rate_limiting
@pytest.mark.security
@skip_if_no_ratelimit
class TestDDoSProtection(RateLimitingTestCase):
    """Test DDoS protection mechanisms"""

    def test_rapid_requests_from_single_ip(self):
        """Test protection against rapid requests from single IP"""
        # Simulate rapid requests
        for i in range(51):  # Assuming global limit is 50 requests per minute
            response = self.client.get("/")

            if i < 50:
                self.assertNotEqual(response.status_code, 429)
            else:
                self.assertEqual(response.status_code, 429)

    def test_suspicious_user_agent_blocking(self):
        """Test blocking of suspicious user agents"""
        suspicious_agents = [
            "bot",
            "crawler",
            "spider",
            "scraper",
            "python-requests",
            "curl",
        ]

        for agent in suspicious_agents:
            response = self.client.get("/", HTTP_USER_AGENT=agent)
            # Should either be blocked or rate limited more aggressively
            self.assertIn(response.status_code, [403, 429])

    def test_request_size_limit(self):
        """Test protection against large request payloads"""
        large_data = "x" * (1024 * 1024 * 2)  # 2MB of data

        response = self.client.post(
            reverse("addAuctions"),
            {"title": "Test", "description": large_data, "starting_bid": "10.00"},
        )

        # Should reject large payloads
        self.assertIn(response.status_code, [400, 413, 429])

    @patch("django.core.cache.cache.get")
    @patch("django.core.cache.cache.set")
    def test_cache_based_rate_limiting(self, mock_cache_set, mock_cache_get):
        """Test that rate limiting uses cache properly"""
        # Mock cache to return None (no existing rate limit)
        mock_cache_get.return_value = None

        self.client.get("/")

        # Verify cache was checked and set
        mock_cache_get.assert_called()
        mock_cache_set.assert_called()

    def test_rate_limit_headers(self):
        """Test that rate limit headers are included in responses"""
        response = self.client.get("/")

        # Check for rate limit headers
        expected_headers = [
            "X-RateLimit-Limit",
            "X-RateLimit-Remaining",
            "X-RateLimit-Reset",
        ]

        for header in expected_headers:
            self.assertIn(header, response.headers)

    def test_rate_limit_bypass_for_staff(self):
        """Test that staff users can bypass rate limits"""
        staff_user = UserFactory(is_staff=True)
        self.client.force_login(staff_user)

        # Make many requests that would normally be rate limited
        for i in range(100):
            response = self.client.get("/")
            # Staff should never be rate limited
            self.assertNotEqual(response.status_code, 429)


@pytest.mark.rate_limiting
class TestRateLimitConfiguration(RateLimitingTestCase):
    """Test rate limiting configuration and settings"""

    def test_rate_limit_settings_exist(self):
        """Test that rate limiting settings are properly configured"""
        self.assertTrue(hasattr(settings, "RATELIMIT_ENABLE"))
        self.assertTrue(hasattr(settings, "RATE_LIMIT_LOGIN_ATTEMPTS"))
        self.assertTrue(hasattr(settings, "RATE_LIMIT_BIDDING"))
        self.assertTrue(hasattr(settings, "RATE_LIMIT_LISTING_CREATION"))
        self.assertTrue(hasattr(settings, "RATE_LIMIT_COMMENTS"))

    def test_middleware_configuration(self):
        """Test that rate limiting middleware is properly configured"""
        middleware_classes = settings.MIDDLEWARE
        self.assertIn("auctions.middleware.RateLimitMiddleware", middleware_classes)
        self.assertIn("auctions.middleware.SecurityMiddleware", middleware_classes)

    def test_cache_configuration(self):
        """Test that cache is configured for rate limiting"""
        self.assertTrue(hasattr(settings, "CACHES"))
        self.assertIn("default", settings.CACHES)


@pytest.mark.rate_limiting
@pytest.mark.integration
@skip_if_no_ratelimit
class TestRateLimitingIntegration(RateLimitingTestCase):
    """Integration tests for rate limiting across different scenarios"""

    def test_multiple_users_same_ip(self):
        """Test rate limiting when multiple users share the same IP"""
        user1 = UserFactory()
        user2 = UserFactory()

        # User 1 makes requests
        self.client.force_login(user1)
        for i in range(25):
            response = self.client.get("/")
            self.assertNotEqual(response.status_code, 429)

        # User 2 from same IP should have separate limits
        self.client.force_login(user2)
        for i in range(25):
            response = self.client.get("/")
            self.assertNotEqual(response.status_code, 429)

    def test_rate_limit_across_different_endpoints(self):
        """Test that rate limits are applied across different endpoints"""
        self.client.force_login(self.user)

        endpoints = [
            reverse("index"),
            reverse("categories"),
        ]

        # Make requests to different endpoints
        request_count = 0
        for endpoint in endpoints:
            for i in range(20):
                response = self.client.get(endpoint)
                request_count += 1

                if request_count < 50:  # Assuming global limit
                    self.assertNotEqual(response.status_code, 429)
                else:
                    self.assertEqual(response.status_code, 429)
                    return

    def test_rate_limit_recovery_after_timeout(self):
        """Test that rate limits reset after timeout period"""
        import time

        # Make requests up to limit
        pass  # Simplified test
        for i in range(50):
            response = self.client.get("/")
            if response.status_code == 429:
                break

        # Verify we hit the limit
        response = self.client.get("/")
        self.assertEqual(response.status_code, 429)

        # In a real scenario, we would wait or mock time passage
        # Then verify limits are reset
        with patch("time.time", return_value=time.time() + 3600):  # 1 hour later
            cache.clear()  # Simulate cache expiration
            response = self.client.get("/")
            self.assertNotEqual(response.status_code, 429)
