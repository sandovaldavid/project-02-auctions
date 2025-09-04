from rest_framework import viewsets, status, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count, Sum, Q
from django.contrib.auth import get_user_model
from auctions.models import Listing, Bid, Watchlist, Comment
from .serializers import (
    UserSerializer,
    UserPublicSerializer,
    ListingSerializer,
    ListingCreateSerializer,
    BidSerializer,
    BidCreateSerializer,
    WatchlistSerializer,
    CommentSerializer,
    ListingStatsSerializer,
)
from .permissions import (
    IsOwnerOrReadOnly,
    IsListingOwnerOrReadOnly,
    IsCommentOwnerOrReadOnly,
    IsBidOwnerOrListingOwner,
    IsWatchlistOwner,
)
from .filters import ListingFilter, BidFilter, CommentFilter

User = get_user_model()


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for User model - read-only access.
    """

    queryset = User.objects.all()
    serializer_class = UserPublicSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    search_fields = ["username", "first_name", "last_name"]
    ordering_fields = ["username", "date_joined"]
    ordering = ["username"]

    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == "list":
            return UserPublicSerializer
        elif self.action == "retrieve" and self.request.user != self.get_object():
            return UserPublicSerializer
        return UserSerializer

    def get_permissions(self):
        """Set permissions based on action"""
        if self.action == "create":
            permission_classes = [permissions.AllowAny]
        elif self.action in ["update", "partial_update", "destroy"]:
            permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
        else:
            permission_classes = [IsAuthenticated]

        return [permission() for permission in permission_classes]

    @action(detail=False, methods=["get", "put", "patch"])
    def me(self, request):
        """Get or update current user profile"""
        if request.method == "GET":
            serializer = self.get_serializer(request.user)
            return Response(serializer.data)

        serializer = self.get_serializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["get"])
    def listings(self, request, pk=None):
        """Get user's listings"""
        user = self.get_object()
        listings = Listing.objects.filter(user=user)

        # Apply filters
        active_only = request.query_params.get("active_only", "false").lower() == "true"
        if active_only:
            listings = listings.filter(active=True)

        page = self.paginate_queryset(listings)
        if page is not None:
            serializer = ListingSerializer(
                page, many=True, context={"request": request}
            )
            return self.get_paginated_response(serializer.data)

        serializer = ListingSerializer(
            listings, many=True, context={"request": request}
        )
        return Response(serializer.data)

    @action(detail=True, methods=["get"])
    def bids(self, request, pk=None):
        """Get user's bids"""
        user = self.get_object()
        bids = (
            Bid.objects.filter(user=user)
            .select_related("listing")
            .order_by("-created_at")
        )

        page = self.paginate_queryset(bids)
        if page is not None:
            serializer = BidSerializer(page, many=True, context={"request": request})
            return self.get_paginated_response(serializer.data)

        serializer = BidSerializer(bids, many=True, context={"request": request})
        return Response(serializer.data)


class ListingViewSet(viewsets.ModelViewSet):
    """ViewSet for Listing model"""

    queryset = Listing.objects.select_related("user").prefetch_related(
        "bids", "comments"
    )
    permission_classes = [IsListingOwnerOrReadOnly]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_class = ListingFilter
    search_fields = ["title", "description", "category"]
    ordering_fields = ["created", "starting_bid", "title"]
    ordering = ["-created"]

    def get_permissions(self):
        """Return appropriate permissions based on action"""
        if self.action in ["bid", "comment"]:
            # For bidding and commenting, only require authentication
            permission_classes = [IsAuthenticated]
        else:
            # For other actions, use default permissions
            permission_classes = self.permission_classes
        return [permission() for permission in permission_classes]

    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == "create":
            return ListingCreateSerializer
        return ListingSerializer

    def get_queryset(self):
        """Filter queryset based on user permissions"""
        queryset = self.queryset

        # Show only active listings for non-owners
        if self.action == "list":
            show_inactive = (
                self.request.query_params.get("show_inactive", "false").lower()
                == "true"
            )
            if not show_inactive:
                queryset = queryset.filter(active=True)

        return queryset

    def perform_create(self, serializer):
        """Set the listing owner to the current user"""
        serializer.save(user=self.request.user)

    def create(self, request, *args, **kwargs):
        """Create a listing and return full serialized data"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        # Use ListingSerializer for the response to include user data
        instance = serializer.instance
        response_serializer = ListingSerializer(instance, context={"request": request})
        headers = self.get_success_headers(serializer.data)
        return Response(
            response_serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    @action(detail=True, methods=["post"])
    def bid(self, request, pk=None):
        """Place a bid on a listing"""
        listing = self.get_object()

        if not listing.active:
            return Response(
                {"error": "Cannot bid on inactive listing"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if listing.user == request.user:
            return Response(
                {"error": "Cannot bid on your own listing"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = BidCreateSerializer(
            data=request.data, context={"request": request, "view": self}
        )
        if serializer.is_valid():
            bid = serializer.save(user=request.user, listing=listing)

            # Update listing's current bid
            listing.current_bid = serializer.validated_data["amount"]
            listing.save()

            return Response(BidSerializer(bid).data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"])
    def close(self, request, pk=None):
        """Close a listing (only owner can do this)"""
        listing = self.get_object()

        if listing.user != request.user:
            return Response(
                {"error": "Only the listing owner can close the auction"},
                status=status.HTTP_403_FORBIDDEN,
            )

        if not listing.active:
            return Response(
                {"error": "Listing is already closed"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Find the highest bidder
        highest_bid = listing.bids.order_by("-amount").first()
        if highest_bid:
            listing.winner = highest_bid.user

        listing.active = False
        listing.save()

        serializer = self.get_serializer(listing)
        return Response(serializer.data)

    @action(detail=True, methods=["get"])
    def bids(self, request, pk=None):
        """Get all bids for a listing"""
        listing = self.get_object()
        bids = listing.bids.select_related("user").order_by("-created_at")

        page = self.paginate_queryset(bids)
        if page is not None:
            serializer = BidSerializer(page, many=True, context={"request": request})
            return self.get_paginated_response(serializer.data)

        serializer = BidSerializer(bids, many=True, context={"request": request})
        return Response(serializer.data)

    @action(detail=True, methods=["get"])
    def comments(self, request, pk=None):
        """Get all comments for a listing"""
        listing = self.get_object()
        comments = listing.comments.select_related("user").order_by("-created")

        page = self.paginate_queryset(comments)
        if page is not None:
            serializer = CommentSerializer(
                page, many=True, context={"request": request}
            )
            return self.get_paginated_response(serializer.data)

        serializer = CommentSerializer(
            comments, many=True, context={"request": request}
        )
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def comment(self, request, pk=None):
        """Add a comment to a listing"""
        listing = self.get_object()

        serializer = CommentSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            serializer.save(user=request.user, listing=listing)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["get"])
    def stats(self, request):
        """Get listing statistics"""
        stats = {
            "total_listings": Listing.objects.count(),
            "active_listings": Listing.objects.filter(active=True).count(),
            "total_bids": Bid.objects.count(),
            "total_value": Listing.objects.aggregate(total=Sum("current_bid"))["total"]
            or 0,
            "categories": dict(
                Listing.objects.values("category")
                .annotate(count=Count("id"))
                .values_list("category", "count")
            ),
        }

        serializer = ListingStatsSerializer(stats)
        return Response(serializer.data)


class BidViewSet(viewsets.ModelViewSet):
    """ViewSet for Bid model"""

    queryset = Bid.objects.select_related("user", "listing")
    serializer_class = BidSerializer
    permission_classes = [IsBidOwnerOrListingOwner]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_class = BidFilter
    search_fields = ["listing__title"]
    ordering_fields = ["created_at", "amount"]
    ordering = ["-created_at"]

    def get_queryset(self):
        """
        Filter bids to only show user's own bids or bids on user's listings.
        """
        user = self.request.user
        return Bid.objects.filter(Q(user=user) | Q(listing__user=user)).select_related(
            "user", "listing"
        )

    def perform_create(self, serializer):
        """Create bid and update listing's current bid"""
        bid = serializer.save(user=self.request.user)

        # Update listing's current bid
        listing = bid.listing
        listing.current_bid = bid.amount
        listing.save()


class WatchlistViewSet(viewsets.ModelViewSet):
    """ViewSet for Watchlist model"""

    queryset = Watchlist.objects.select_related("user", "listing")
    serializer_class = WatchlistSerializer
    permission_classes = [IsWatchlistOwner]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["listing"]
    ordering_fields = ["created_at"]
    ordering = ["-created_at"]

    def get_queryset(self):
        """Return only current user's watchlist"""
        return Watchlist.objects.filter(user=self.request.user).select_related(
            "listing"
        )

    def perform_create(self, serializer):
        """Add listing to user's watchlist"""
        serializer.save(user=self.request.user)

    @action(detail=False, methods=["post"])
    def toggle(self, request):
        """Toggle watchlist status for a listing"""
        listing_id = request.data.get("listing_id")

        if not listing_id:
            return Response(
                {"error": "listing_id is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            listing = Listing.objects.get(id=listing_id, active=True)
        except Listing.DoesNotExist:
            return Response(
                {"error": "Listing not found or inactive"},
                status=status.HTTP_404_NOT_FOUND,
            )

        watchlist_item, created = Watchlist.objects.get_or_create(
            user=request.user, listing=listing
        )

        if not created:
            watchlist_item.delete()
            return Response({"status": "removed", "watching": False})

        serializer = self.get_serializer(watchlist_item)
        return Response(
            {"status": "added", "watching": True, "watchlist_item": serializer.data},
            status=status.HTTP_201_CREATED,
        )


class CommentViewSet(viewsets.ModelViewSet):
    """ViewSet for Comment model"""

    queryset = Comment.objects.select_related("user", "listing")
    serializer_class = CommentSerializer
    permission_classes = [IsCommentOwnerOrReadOnly]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_class = CommentFilter
    search_fields = ["text"]
    ordering_fields = ["created"]
    ordering = ["-created"]

    def get_queryset(self):
        """Return comments based on user permissions"""
        return Comment.objects.select_related("user", "listing")

    def perform_create(self, serializer):
        """Set the comment author to the current user"""
        serializer.save(user=self.request.user)


# Custom JWT Views
class CustomTokenObtainPairView(TokenObtainPairView):
    """Custom JWT token obtain view with additional user data"""

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)

        if response.status_code == 200:
            # Add user data to response
            from django.contrib.auth import authenticate

            username = request.data.get("username")
            password = request.data.get("password")
            user = authenticate(username=username, password=password)

            if user:
                user_serializer = UserPublicSerializer(user)
                response.data["user"] = user_serializer.data

        return response


class CustomTokenRefreshView(TokenRefreshView):
    """Custom JWT token refresh view"""

    pass
