from rest_framework import serializers
from django.contrib.auth import get_user_model
from auctions.models import Listing, Bid, Watchlist, Comment

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model"""

    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "password",
            "date_joined",
        )
        read_only_fields = ("id", "date_joined")
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        """Create user with encrypted password"""
        password = validated_data.pop("password")
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        """Update user, handling password separately"""
        password = validated_data.pop("password", None)
        user = super().update(instance, validated_data)

        if password:
            user.set_password(password)
            user.save()

        return user


class UserPublicSerializer(serializers.ModelSerializer):
    """Public serializer for User model (limited fields)"""

    class Meta:
        model = User
        fields = ("id", "username", "first_name", "last_name", "date_joined")
        read_only_fields = ("id", "username", "first_name", "last_name", "date_joined")


class BidSerializer(serializers.ModelSerializer):
    """Serializer for Bid model"""

    user = UserPublicSerializer(read_only=True)
    listing_title = serializers.CharField(source="listing.title", read_only=True)

    class Meta:
        model = Bid
        fields = ("id", "user", "listing", "listing_title", "amount", "created_at")
        read_only_fields = ("id", "user", "created_at")

    def validate_amount(self, value):
        """Validate bid amount"""
        if value <= 0:
            raise serializers.ValidationError("Bid amount must be positive.")

        # Check if listing exists and bid is higher than current highest bid
        listing_id = self.context["view"].kwargs.get("pk") or self.initial_data.get(
            "listing"
        )
        if listing_id:
            try:
                listing = Listing.objects.get(id=listing_id)
                if not listing.active:
                    raise serializers.ValidationError("Cannot bid on inactive listing.")

                current_highest = listing.current_bid
                if current_highest and value <= current_highest:
                    raise serializers.ValidationError(
                        f"Bid must be higher than current highest bid of ${current_highest}."
                    )
                elif not current_highest and value < listing.starting_bid:
                    raise serializers.ValidationError(
                        f"Bid must be at least ${listing.starting_bid}."
                    )
            except Listing.DoesNotExist:
                raise serializers.ValidationError("Invalid listing.")

        return value


class CommentSerializer(serializers.ModelSerializer):
    """Serializer for Comment model"""

    user = UserPublicSerializer(read_only=True)
    listing_title = serializers.CharField(source="listing.title", read_only=True)

    class Meta:
        model = Comment
        fields = ("id", "user", "listing", "listing_title", "text", "created")
        read_only_fields = ("id", "user", "created")

    def validate_text(self, value):
        """Validate comment text"""
        if len(value.strip()) < 5:
            raise serializers.ValidationError(
                "Comment must be at least 5 characters long."
            )
        return value.strip()


class ListingSerializer(serializers.ModelSerializer):
    """Serializer for Listing model"""

    user = UserPublicSerializer(read_only=True)
    current_bid = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True
    )
    bid_count = serializers.SerializerMethodField()
    time_remaining = serializers.SerializerMethodField()
    is_watched = serializers.SerializerMethodField()
    winner = UserPublicSerializer(read_only=True)
    latest_bids = BidSerializer(many=True, read_only=True, source="bids")
    comments = CommentSerializer(many=True, read_only=True)

    class Meta:
        model = Listing
        fields = (
            "id",
            "title",
            "description",
            "starting_bid",
            "current_bid",
            "image",
            "category",
            "active",
            "created",
            "user",
            "winner",
            "bid_count",
            "time_remaining",
            "is_watched",
            "latest_bids",
            "comments",
        )
        read_only_fields = ("id", "created", "user", "current_bid", "winner")

    def get_bid_count(self, obj):
        """Get number of bids for this listing"""
        return obj.bids.count()

    def get_time_remaining(self, obj):
        """Get time remaining for auction (placeholder - would need end_time field)"""
        # This would require adding an end_time field to the Listing model
        return None

    def get_is_watched(self, obj):
        """Check if current user is watching this listing"""
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return Watchlist.objects.filter(user=request.user, listing=obj).exists()
        return False

    def validate_starting_bid(self, value):
        """Validate starting bid amount"""
        if value <= 0:
            raise serializers.ValidationError("Starting bid must be positive.")
        return value

    def validate_image(self, value):
        """Validate image URL format"""
        if value and not (value.startswith("http://") or value.startswith("https://")):
            raise serializers.ValidationError(
                "Image URL must start with http:// or https://"
            )
        return value


class ListingCreateSerializer(serializers.ModelSerializer):
    """Simplified serializer for creating listings"""

    class Meta:
        model = Listing
        fields = ("title", "description", "starting_bid", "image", "category")

    def validate_starting_bid(self, value):
        """Validate starting bid amount"""
        if value <= 0:
            raise serializers.ValidationError("Starting bid must be positive.")
        return value


class BidCreateSerializer(serializers.ModelSerializer):
    """Simplified serializer for creating bids through listing endpoint"""

    user = UserPublicSerializer(read_only=True)

    class Meta:
        model = Bid
        fields = ("id", "user", "amount", "created_at")
        read_only_fields = ("id", "user", "created_at")

    def validate_amount(self, value):
        """Validate bid amount against listing requirements"""
        if value <= 0:
            raise serializers.ValidationError("Bid amount must be positive.")

        # Get listing from view context
        view = self.context.get("view")
        if view and hasattr(view, "get_object"):
            try:
                listing_id = view.kwargs.get("pk")
                if listing_id:
                    listing = Listing.objects.get(pk=listing_id)

                    # Check against starting bid
                    if value < listing.starting_bid:
                        raise serializers.ValidationError(
                            f"Bid must be at least {listing.starting_bid} (starting bid)."
                        )

                    # Check against current highest bid
                    if listing.current_bid and value <= listing.current_bid:
                        raise serializers.ValidationError(
                            f"Bid must be higher than current bid of {listing.current_bid}."
                        )
            except Listing.DoesNotExist:
                raise serializers.ValidationError("Invalid listing.")

        return value


class WatchlistSerializer(serializers.ModelSerializer):
    """Serializer for Watchlist model"""

    listing = ListingSerializer(read_only=True)
    listing_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Watchlist
        fields = ("id", "listing", "listing_id", "created_at")
        read_only_fields = ("id", "created_at")

    def validate_listing_id(self, value):
        """Validate that listing exists and is active"""
        try:
            listing = Listing.objects.get(id=value)
            if not listing.active:
                raise serializers.ValidationError("Cannot watch inactive listing.")
            return value
        except Listing.DoesNotExist:
            raise serializers.ValidationError("Listing does not exist.")

    def create(self, validated_data):
        """Create watchlist entry"""
        listing_id = validated_data.pop("listing_id")
        listing = Listing.objects.get(id=listing_id)
        user = self.context["request"].user

        # Check if already watching
        if Watchlist.objects.filter(user=user, listing=listing).exists():
            raise serializers.ValidationError("Already watching this listing.")

        return Watchlist.objects.create(user=user, listing=listing)


class ListingStatsSerializer(serializers.Serializer):
    """Serializer for listing statistics"""

    total_listings = serializers.IntegerField()
    active_listings = serializers.IntegerField()
    total_bids = serializers.IntegerField()
    total_value = serializers.DecimalField(max_digits=15, decimal_places=2)
    categories = serializers.DictField()
