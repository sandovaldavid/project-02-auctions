from django.http import HttpResponse


class RateLimitMiddleware:
    """Middleware to add rate limiting headers to responses"""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Add rate limiting headers to all responses
        if not hasattr(response, "status_code") or response.status_code != 429:
            # Add default rate limit headers for successful requests
            response["X-RateLimit-Limit"] = "20"
            response["X-RateLimit-Remaining"] = "19"
            response["X-RateLimit-Reset"] = "60"

        return response


class SecurityMiddleware:
    """Middleware for additional security features"""

    def __init__(self, get_response):
        self.get_response = get_response
        self.suspicious_user_agents = [
            "bot",
            "crawler",
            "spider",
            "scraper",
            "curl",
            "wget",
        ]

    def __call__(self, request):
        # Check request size (basic protection) - do this before processing
        content_length = request.META.get("CONTENT_LENGTH")
        if content_length and int(content_length) > 1024 * 1024:  # 1MB limit
            return HttpResponse("Request too large", status=413)

        # Process the request to get user authentication info
        response = self.get_response(request)

        # Check for suspicious user agents after authentication is processed
        user_agent = request.META.get("HTTP_USER_AGENT", "").lower()
        if any(agent in user_agent for agent in self.suspicious_user_agents):
            # Allow staff users to bypass this check
            if not (
                hasattr(request, "user")
                and request.user.is_authenticated
                and request.user.is_staff
            ):
                return HttpResponse(
                    "Access denied: Suspicious user agent detected.", status=403
                )

        # Add security headers
        response["X-Content-Type-Options"] = "nosniff"
        response["X-Frame-Options"] = "DENY"
        response["X-XSS-Protection"] = "1; mode=block"

        return response
