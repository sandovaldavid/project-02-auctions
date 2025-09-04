import django_filters
from django.db.models import Q
from auctions.models import Listing, Bid, Comment


class ListingFilter(django_filters.FilterSet):
    """
    Filter for Listing model with advanced search capabilities.
    """

    title = django_filters.CharFilter(lookup_expr="icontains")
    description = django_filters.CharFilter(lookup_expr="icontains")
    category = django_filters.CharFilter(lookup_expr="icontains")
    min_price = django_filters.NumberFilter(
        field_name="starting_bid", lookup_expr="gte"
    )
    max_price = django_filters.NumberFilter(
        field_name="starting_bid", lookup_expr="lte"
    )
    active = django_filters.BooleanFilter()
    user = django_filters.CharFilter(
        field_name="user__username", lookup_expr="icontains"
    )

    # Date filters
    created_after = django_filters.DateTimeFilter(
        field_name="created", lookup_expr="gte"
    )
    created_before = django_filters.DateTimeFilter(
        field_name="created", lookup_expr="lte"
    )

    # Search across multiple fields
    search = django_filters.CharFilter(method="filter_search")

    # Filter by bid count range
    min_bids = django_filters.NumberFilter(method="filter_min_bids")
    max_bids = django_filters.NumberFilter(method="filter_max_bids")

    # Filter by current price range (highest bid or starting bid)
    min_current_price = django_filters.NumberFilter(method="filter_min_current_price")
    max_current_price = django_filters.NumberFilter(method="filter_max_current_price")

    class Meta:
        model = Listing
        fields = [
            "title",
            "description",
            "category",
            "min_price",
            "max_price",
            "active",
            "user",
            "created_after",
            "created_before",
            "search",
            "min_bids",
            "max_bids",
            "min_current_price",
            "max_current_price",
        ]

    def filter_search(self, queryset, name, value):
        """
        Search across title, description, and category.
        """
        return queryset.filter(
            Q(title__icontains=value)
            | Q(description__icontains=value)
            | Q(category__icontains=value)
        )

    def filter_min_bids(self, queryset, name, value):
        """
        Filter by minimum number of bids.
        """
        return queryset.annotate(bid_count=django_filters.Count("bids")).filter(
            bid_count__gte=value
        )

    def filter_max_bids(self, queryset, name, value):
        """
        Filter by maximum number of bids.
        """
        return queryset.annotate(bid_count=django_filters.Count("bids")).filter(
            bid_count__lte=value
        )

    def filter_min_current_price(self, queryset, name, value):
        """
        Filter by minimum current price (highest bid or starting bid).
        """
        from django.db.models import Max, Case, When, F

        return queryset.annotate(
            current_price=Case(
                When(bids__isnull=True, then=F("starting_bid")),
                default=Max("bids__amount"),
            )
        ).filter(current_price__gte=value)

    def filter_max_current_price(self, queryset, name, value):
        """
        Filter by maximum current price (highest bid or starting bid).
        """
        from django.db.models import Max, Case, When, F

        return queryset.annotate(
            current_price=Case(
                When(bids__isnull=True, then=F("starting_bid")),
                default=Max("bids__amount"),
            )
        ).filter(current_price__lte=value)


class BidFilter(django_filters.FilterSet):
    """
    Filter for Bid model.
    """

    listing = django_filters.NumberFilter(field_name="listing__id")
    listing_title = django_filters.CharFilter(
        field_name="listing__title", lookup_expr="icontains"
    )
    user = django_filters.CharFilter(
        field_name="user__username", lookup_expr="icontains"
    )
    min_amount = django_filters.NumberFilter(field_name="amount", lookup_expr="gte")
    max_amount = django_filters.NumberFilter(field_name="amount", lookup_expr="lte")

    # Date filters
    created_after = django_filters.DateTimeFilter(
        field_name="created", lookup_expr="gte"
    )
    created_before = django_filters.DateTimeFilter(
        field_name="created", lookup_expr="lte"
    )

    class Meta:
        model = Bid
        fields = [
            "listing",
            "listing_title",
            "user",
            "min_amount",
            "max_amount",
            "created_after",
            "created_before",
        ]


class CommentFilter(django_filters.FilterSet):
    """
    Filter for Comment model.
    """

    listing = django_filters.NumberFilter(field_name="listing__id")
    listing_title = django_filters.CharFilter(
        field_name="listing__title", lookup_expr="icontains"
    )
    user = django_filters.CharFilter(
        field_name="user__username", lookup_expr="icontains"
    )
    text = django_filters.CharFilter(lookup_expr="icontains")

    # Date filters
    created_after = django_filters.DateTimeFilter(
        field_name="created", lookup_expr="gte"
    )
    created_before = django_filters.DateTimeFilter(
        field_name="created", lookup_expr="lte"
    )

    class Meta:
        model = Comment
        fields = [
            "listing",
            "listing_title",
            "user",
            "text",
            "created_after",
            "created_before",
        ]
