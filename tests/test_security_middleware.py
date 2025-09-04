import pytest
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from tests.conftest import UserFactory

User = get_user_model()


@pytest.mark.security
class TestSecurityMiddleware(TestCase):
    """Test security middleware functionality"""

    def setUp(self):
        self.client = Client()
        self.user = UserFactory()

    def test_suspicious_user_agent_blocking(self):
        """Test that suspicious user agents are blocked"""
        suspicious_agents = ["bot", "crawler", "spider", "scraper", "curl", "wget"]

        for agent in suspicious_agents:
            response = self.client.get(reverse("index"), HTTP_USER_AGENT=agent)
            # Should be blocked (403) unless user is staff
            self.assertEqual(response.status_code, 403)

    def test_staff_bypass_user_agent_blocking(self):
        """Test that staff users can bypass user agent blocking"""
        staff_user = UserFactory(is_staff=True)
        self.client.force_login(staff_user)

        response = self.client.get(reverse("index"), HTTP_USER_AGENT="bot")
        # Staff should not be blocked
        self.assertEqual(response.status_code, 200)

    def test_normal_user_agent_allowed(self):
        """Test that normal user agents are allowed"""
        normal_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
        ]

        for agent in normal_agents:
            response = self.client.get(reverse("index"), HTTP_USER_AGENT=agent)
            self.assertEqual(response.status_code, 200)

    def test_security_headers_added(self):
        """Test that security headers are added to responses"""
        response = self.client.get(reverse("index"))

        # Check for security headers
        self.assertIn("X-Content-Type-Options", response)
        self.assertEqual(response["X-Content-Type-Options"], "nosniff")

        self.assertIn("X-Frame-Options", response)
        self.assertEqual(response["X-Frame-Options"], "DENY")

        self.assertIn("X-XSS-Protection", response)
        self.assertEqual(response["X-XSS-Protection"], "1; mode=block")

    def test_rate_limit_headers_added(self):
        """Test that rate limit headers are added to responses"""
        response = self.client.get(reverse("index"))

        # Check for rate limiting headers
        self.assertIn("X-RateLimit-Limit", response)
        self.assertIn("X-RateLimit-Remaining", response)
        self.assertIn("X-RateLimit-Reset", response)

    def test_request_size_limit(self):
        """Test that large requests are rejected"""
        # Create a large payload (over 1MB)
        large_data = {
            "title": "Test",
            "description": "x" * (1024 * 1024 + 1),  # Just over 1MB
            "starting_bid": 10.00,
            "category": "Test Category",
        }

        self.client.force_login(self.user)
        response = self.client.post(reverse("addAuctions"), large_data)

        # Should be rejected with 413 (Payload Too Large)
        self.assertEqual(response.status_code, 413)

    def test_normal_request_size_allowed(self):
        """Test that normal-sized requests are allowed"""
        normal_data = {
            "title": "Test Listing",
            "description": "A normal description",
            "starting_bid": 10.00,
            "category": "Test Category",
        }

        self.client.force_login(self.user)
        response = self.client.post(reverse("addAuctions"), normal_data)

        # Should not be rejected due to size (may fail for other reasons)
        self.assertNotEqual(response.status_code, 413)
