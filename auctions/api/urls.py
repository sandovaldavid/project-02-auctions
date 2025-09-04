from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenVerifyView

from .views import (
    UserViewSet,
    ListingViewSet,
    BidViewSet,
    CommentViewSet,
    WatchlistViewSet,
    CustomTokenObtainPairView,
    CustomTokenRefreshView,
)

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r"users", UserViewSet)
router.register(r"listings", ListingViewSet)
router.register(r"bids", BidViewSet)
router.register(r"comments", CommentViewSet)
router.register(r"watchlist", WatchlistViewSet)

# The API URLs are now determined automatically by the router.
urlpatterns = [
    # API endpoints
    path("", include(router.urls)),
    # Authentication endpoints
    path("auth/login", CustomTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("auth/refresh/", CustomTokenRefreshView.as_view(), name="token_refresh"),
    path("auth/verify/", TokenVerifyView.as_view(), name="token_verify"),
    # DRF browsable API authentication
    path("auth/", include("rest_framework.urls")),
]
