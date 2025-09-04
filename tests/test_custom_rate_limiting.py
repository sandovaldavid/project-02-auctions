import pytest
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.cache import cache
from tests.conftest import UserFactory

User = get_user_model()


@pytest.mark.rate_limiting
class TestCustomRateLimiting(TestCase):
    """Test custom rate limiting implementation"""

    def setUp(self):
        self.client = Client()
        self.user = UserFactory()
        # Clear cache before each test
        cache.clear()

    def test_rate_limit_headers_present(self):
        """Test that rate limit headers are added to responses"""
        response = self.client.get(reverse("index"))

        # Check for rate limiting headers
        self.assertIn("X-RateLimit-Limit", response)
        self.assertIn("X-RateLimit-Remaining", response)
        self.assertIn("X-RateLimit-Reset", response)

    def test_login_rate_limiting_basic(self):
        """Test basic login rate limiting functionality"""
        login_url = reverse("login")

        # Make multiple login attempts
        for i in range(3):
            response = self.client.post(
                login_url, {"username": "testuser", "password": "wrongpassword"}
            )
            # Should not be rate limited yet (limit is 5)
            self.assertNotEqual(response.status_code, 429)

    def test_index_rate_limiting_basic(self):
        """Test basic index page rate limiting functionality"""
        index_url = reverse("index")

        # Make multiple requests
        for i in range(10):
            response = self.client.get(index_url)
            # Should not be rate limited yet (limit is 20)
            self.assertNotEqual(response.status_code, 429)

    def test_security_headers_present(self):
        """Test that security headers are added to responses"""
        response = self.client.get(reverse("index"))

        # Check for security headers
        self.assertIn("X-Content-Type-Options", response)
        self.assertEqual(response["X-Content-Type-Options"], "nosniff")

        self.assertIn("X-Frame-Options", response)
        self.assertEqual(response["X-Frame-Options"], "DENY")

        self.assertIn("X-XSS-Protection", response)
        self.assertEqual(response["X-XSS-Protection"], "1; mode=block")

    def test_authenticated_user_rate_limiting(self):
        """Test rate limiting for authenticated users"""
        self.client.force_login(self.user)

        # Test listing creation rate limiting
        create_url = reverse("addAuctions")

        # Make multiple requests
        for i in range(3):
            response = self.client.post(
                create_url,
                {
                    "title": f"Test Listing {i}",
                    "description": "Test description",
                    "starting_bid": 10.00,
                    "category": "Test Category",
                },
            )
            # Should not be rate limited yet (limit is 5)
            self.assertNotEqual(response.status_code, 429)

    def test_cache_functionality(self):
        """Test that cache is working for rate limiting"""
        # Set a test value in cache
        cache.set("test_key", "test_value", 60)

        # Verify it can be retrieved
        self.assertEqual(cache.get("test_key"), "test_value")

        # Clear cache
        cache.clear()

        # Verify it's gone
        self.assertIsNone(cache.get("test_key"))
