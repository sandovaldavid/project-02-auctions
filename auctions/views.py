from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.db import IntegrityError
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.conf import settings
from django.core.cache import cache
from django.utils import timezone
from django.db.models import Count, Sum, Avg
from functools import wraps

from .forms import ListingForm, BidForm, CommentForm
from .models import User, Listing, Watchlist


def custom_ratelimit(key="ip", rate="20/m", method="GET"):
    def decorator(func):
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            # Check if rate limiting is enabled
            if not getattr(settings, "RATELIMIT_ENABLE", True):
                return func(request, *args, **kwargs)

            if request.method != method:
                return func(request, *args, **kwargs)

            # Extract rate limit values
            limit, period = rate.split("/")
            limit = int(limit)
            period_seconds = {"s": 1, "m": 60, "h": 3600, "d": 86400}[period[-1]]

            # Generate cache key
            if key == "ip":
                cache_key = f"ratelimit:{request.META.get('REMOTE_ADDR', 'unknown')}"
            elif key == "user" and request.user.is_authenticated:
                cache_key = f"ratelimit:user:{request.user.id}"
            else:
                cache_key = "ratelimit:anonymous"

            # Check current count
            current_count = cache.get(cache_key, 0)
            if current_count >= limit:
                return HttpResponse(
                    "Rate limit exceeded. Please try again later.",
                    status=429,
                    headers={
                        "X-RateLimit-Limit": str(limit),
                        "X-RateLimit-Remaining": "0",
                        "X-RateLimit-Reset": str(period_seconds),
                    },
                )

            # Increment counter
            cache.set(cache_key, current_count + 1, period_seconds)
            return func(request, *args, **kwargs)

        return wrapper

    return decorator


@custom_ratelimit(
    key="ip", rate=getattr(settings, "RATE_LIMIT_API_ANONYMOUS", "20/m"), method="GET"
)
def index(request):
    list_user = Listing.objects.filter(active=True).order_by("-created")
    paginator = Paginator(list_user, 10)
    page_number = request.GET.get("page")
    page_listings = paginator.get_page(page_number)
    return render(request, "auctions/index.html", {"listings": page_listings})


@custom_ratelimit(
    key="ip", rate=getattr(settings, "RATE_LIMIT_LOGIN_ATTEMPTS", "5/m"), method="POST"
)
def login_view(request):
    if request.method == "POST":
        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        return render(
            request,
            "auctions/login.html",
            {"message": "Invalid username and/or password."},
        )
    return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(
                request, "auctions/register.html", {"message": "Passwords must match."}
            )

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(
                request,
                "auctions/register.html",
                {"message": "Username already taken."},
            )
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    return render(request, "auctions/register.html")


@login_required
@custom_ratelimit(
    key="user",
    rate=getattr(settings, "RATE_LIMIT_LISTING_CREATION", "5/m"),
    method="POST",
)
def new_auctions(request):
    category_choices = ListingForm.CATEGORY_CHOICES
    if request.method == "POST":
        form = ListingForm(request.POST)
        if form.is_valid():
            # Set the logged-in user
            listing = form.save(commit=False)  # Don't save yet
            listing.user = request.user  # Set the user
            listing.save()  # Now save the Listing}
            messages.success(request, "Your listing has been created.")
            return redirect("index")
        messages.error(request, "There was an error with created your listing.")
        return render(
            request,
            "auctions/newAuctions.html",
            {"form": form, "category_choices": category_choices},
        )
    form = ListingForm()
    return render(
        request,
        "auctions/newAuctions.html",
        {"form": form, "category_choices": category_choices},
    )


def listing(request, listing_id):
    auction = get_object_or_404(Listing, id=listing_id)
    comments = auction.comments.all()
    form = CommentForm()
    return render(
        request,
        "auctions/auction.html",
        {"listing": auction, "comments": comments, "form": form},
    )


@login_required
@custom_ratelimit(
    key="user", rate=getattr(settings, "RATE_LIMIT_BIDDING", "10/m"), method="POST"
)
def bid(request, listing_id):
    auction = get_object_or_404(Listing, pk=listing_id)
    comment_auction = auction.comments.all().count()
    if request.method == "POST":
        bid_form = BidForm(request.POST)
        if bid_form.is_valid():
            bid_value = bid_form.cleaned_data["amount"]
            try:
                auction.place_bid(user=request.user, bid_value=bid_value)
                messages.success(request, "Your bid has been placed successfully.")
                messages.info(
                    request,
                    f"({comment_auction}) bid(s) so far. Your bid is the current bid.",
                )
                return redirect("listing", listing_id=listing_id)
            except ValidationError as e:
                bid_form.add_error("amount", str(e)[2:-2])
        else:
            messages.error(
                request,
                "There was an error with your bid. Please review and try again.",
            )
        return render(
            request,
            "auctions/auction.html",
            {"listing": auction, "form": bid_form, "comments": auction.comments.all()},
        )
    return None


def watchlist(request, listing_id):
    """Add item to watchlist"""
    user = request.user
    if request.method == "POST":
        current_listing = Listing.objects.get(pk=listing_id)
        watchlist_item, created = Watchlist.objects.get_or_create(
            user=user, listing=current_listing, defaults={"active": True}
        )

        if created:
            messages.success(
                request, f"'{current_listing.title}' added to your watchlist."
            )
        else:
            # If it exists but is inactive, activate it
            if not watchlist_item.active:
                watchlist_item.active = True
                watchlist_item.save()
                messages.success(
                    request, f"'{current_listing.title}' added back to your watchlist."
                )
            else:
                messages.info(
                    request, f"'{current_listing.title}' is already in your watchlist."
                )

        # Redirect back to the referring page or to the listing page
        referer = request.META.get("HTTP_REFERER")
        if referer and "my-watchlist" in referer:
            return HttpResponseRedirect(reverse("my_watchlist"))
        else:
            return HttpResponseRedirect(reverse("listing", args=[listing_id]))

    # If GET request, redirect to listing page
    return HttpResponseRedirect(reverse("listing", args=[listing_id]))


@login_required
def my_watchlist(request):
    """Display user's watchlist"""
    user = request.user
    listings_in_watchlist = Listing.objects.filter(
        watchlist__user=user, watchlist__active=True
    ).order_by("-created")
    paginator = Paginator(listings_in_watchlist, 10)
    page_number = request.GET.get("page")
    page_listings = paginator.get_page(page_number)
    return render(request, "auctions/watchList.html", {"listings": page_listings})


def watchlist_remove(request, listing_id):
    user = request.user
    current_listing = Listing.objects.get(pk=listing_id)
    try:
        watchlist_item = Watchlist.objects.get(user=user, listing=current_listing)
        watchlist_item.active = False  # Desactivar en lugar de eliminar
        watchlist_item.save()
        messages.success(
            request, f"'{current_listing.title}' removed from your watchlist."
        )
    except Watchlist.DoesNotExist:
        messages.error(request, "Item not found in your watchlist.")

    # Redirect back to the referring page or to the listing page
    referer = request.META.get("HTTP_REFERER")
    if referer and "my-watchlist" in referer:
        # If coming from watchlist page, redirect back to watchlist
        return HttpResponseRedirect(reverse("my_watchlist"))
    else:
        # If coming from listing page, redirect back to listing
        return HttpResponseRedirect(reverse("listing", args=[listing_id]))


def close_auction(request, listing_id):
    listing = get_object_or_404(Listing, id=listing_id)

    if request.user != listing.user:
        messages.error(request, "You are not authorized to close this auction.")
        return redirect("listing", listing_id=listing_id)
    highest_bid = listing.bids.order_by("-amount").first()
    if highest_bid:
        listing.winner = highest_bid.user
    else:
        messages.warning(request, "No bids were placed on this listing.")
    listing.active = False
    listing.save()
    messages.success(request, "The auction has been closed.")
    return redirect("listing", listing_id=listing_id)


@custom_ratelimit(
    key="ip", rate=getattr(settings, "RATE_LIMIT_API_ANONYMOUS", "20/m"), method="GET"
)
def categories(request):
    category = request.GET.get("category")
    if category:
        listings = Listing.objects.filter(category=category, active=True).order_by(
            "-created"
        )
    else:
        listings = Listing.objects.filter(active=True).order_by("-created")
    paginator = Paginator(listings, 10)
    page_number = request.GET.get("page")
    listings = paginator.get_page(page_number)
    return render(
        request,
        "auctions/categories.html",
        {
            "listings": listings,
            "category_choices": ListingForm.CATEGORY_CHOICES,
            "selected_category": category,
        },
    )


@custom_ratelimit(
    key="ip", rate=getattr(settings, "RATE_LIMIT_API_ANONYMOUS", "30/m"), method="GET"
)
def search(request):
    """Advanced search with multiple filters and sorting options"""
    query = request.GET.get("q", "").strip()
    category = request.GET.get("category", "")
    min_price = request.GET.get("min_price", "")
    max_price = request.GET.get("max_price", "")
    sort_by = request.GET.get("sort_by", "newest")

    # Start with active listings
    listings = Listing.objects.filter(active=True)

    # Apply search query
    if query:
        from django.db.models import Q

        listings = listings.filter(
            Q(title__icontains=query) | Q(description__icontains=query)
        )

    # Apply category filter
    if category:
        listings = listings.filter(category=category)

    # Apply price filters
    if min_price:
        try:
            min_price_decimal = float(min_price)
            listings = listings.filter(starting_bid__gte=min_price_decimal)
        except ValueError:
            pass

    if max_price:
        try:
            max_price_decimal = float(max_price)
            listings = listings.filter(starting_bid__lte=max_price_decimal)
        except ValueError:
            pass

    # Apply sorting
    if sort_by == "newest":
        listings = listings.order_by("-created")
    elif sort_by == "oldest":
        listings = listings.order_by("created")
    elif sort_by == "price_low":
        listings = listings.order_by("starting_bid")
    elif sort_by == "price_high":
        listings = listings.order_by("-starting_bid")
    elif sort_by == "title_az":
        listings = listings.order_by("title")
    elif sort_by == "title_za":
        listings = listings.order_by("-title")
    else:
        listings = listings.order_by("-created")

    # Pagination
    paginator = Paginator(listings, 12)
    page_number = request.GET.get("page")
    page_listings = paginator.get_page(page_number)

    # Get search statistics
    total_results = listings.count()

    context = {
        "listings": page_listings,
        "query": query,
        "category": category,
        "min_price": min_price,
        "max_price": max_price,
        "sort_by": sort_by,
        "total_results": total_results,
        "category_choices": ListingForm.CATEGORY_CHOICES,
        "sort_choices": [
            ("newest", "Newest First"),
            ("oldest", "Oldest First"),
            ("price_low", "Price: Low to High"),
            ("price_high", "Price: High to Low"),
            ("title_az", "Title: A-Z"),
            ("title_za", "Title: Z-A"),
        ],
    }

    return render(request, "auctions/search.html", context)


@custom_ratelimit(
    key="ip", rate=getattr(settings, "RATE_LIMIT_API_ANONYMOUS", "60/m"), method="GET"
)
def search_autocomplete(request):
    """AJAX endpoint for search autocomplete suggestions"""
    # Check for AJAX header
    if not request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JsonResponse({"error": "AJAX request required"}, status=400)

    query = request.GET.get("q", "").strip()

    if len(query) < 2:
        return JsonResponse({"suggestions": []})

    # Get title suggestions
    title_suggestions = (
        Listing.objects.filter(title__icontains=query, active=True)
        .values_list("title", flat=True)
        .distinct()[:5]
    )

    # Get category suggestions
    category_suggestions = []
    for value, display in ListingForm.CATEGORY_CHOICES:
        if query.lower() in display.lower():
            category_suggestions.append(display)

    suggestions = {
        "titles": list(title_suggestions),
        "categories": category_suggestions[:3],
    }

    return JsonResponse({"suggestions": suggestions})


@login_required
@custom_ratelimit(
    key="user", rate=getattr(settings, "RATE_LIMIT_COMMENTS", "10/m"), method="POST"
)
def comment(request, listing_id):
    auction = get_object_or_404(Listing, pk=listing_id)
    comments = auction.comments.filter(listing=auction)
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment_auction = form.save(commit=False)
            comment_auction.user = request.user
            comment_auction.listing = auction
            comment_auction.save()
            messages.success(request, "Your comment has been added.")
        else:
            messages.error(request, "There was an error with your comment.")
            return render(
                request,
                "auctions/auction.html",
                {"listing": auction, "comments": comments, "form": form},
            )
    return redirect("listing", listing_id=listing_id)


@login_required
def notifications(request):
    """Display user notifications"""
    notifications = request.user.notifications.all().order_by("-created_at")
    return render(
        request, "auctions/notifications.html", {"notifications": notifications}
    )


@login_required
def profile(request):
    """Display user profile"""
    user = request.user

    # Get user statistics
    user_listings = Listing.objects.filter(user=user)
    total_listings = user_listings.count()
    active_listings = user_listings.filter(active=True).count()
    closed_listings = user_listings.filter(active=False).count()

    # Get user bids
    from .models import Bid

    user_bids = Bid.objects.filter(user=user).count()

    # Get watchlist count
    watchlist_count = Watchlist.objects.filter(user=user, active=True).count()

    context = {
        "user": user,
        "total_listings": total_listings,
        "active_listings": active_listings,
        "closed_listings": closed_listings,
        "user_bids": user_bids,
        "watchlist_count": watchlist_count,
    }

    return render(request, "auctions/profile.html", context)


@login_required
def dashboard(request):
    """Display business intelligence dashboard with KPIs"""
    from .models import Bid

    # General KPIs
    total_listings = Listing.objects.count()
    active_listings = Listing.objects.filter(active=True).count()
    total_users = User.objects.count()
    total_bids = Bid.objects.count()

    # User-specific KPIs
    user_listings = Listing.objects.filter(user=request.user)
    user_active_listings = user_listings.filter(active=True).count()
    user_total_listings = user_listings.count()
    user_bids = Bid.objects.filter(user=request.user).count()

    # Revenue and bidding analytics
    total_bid_amount = Bid.objects.aggregate(total=Sum("amount"))["total"] or 0
    avg_bid_amount = Bid.objects.aggregate(avg=Avg("amount"))["avg"] or 0

    # Category distribution
    category_stats = (
        Listing.objects.values("category")
        .annotate(count=Count("id"))
        .order_by("-count")[:5]
    )

    # Recent activity
    recent_listings = Listing.objects.order_by("-created")[:5]
    recent_bids = Bid.objects.select_related("listing", "user").order_by("-created_at")[
        :5
    ]

    # Monthly trends (last 6 months)
    from datetime import timedelta

    six_months_ago = timezone.now() - timedelta(days=180)

    monthly_listings = (
        Listing.objects.filter(created__gte=six_months_ago)
        .extra(select={"month": "strftime('%%Y-%%m', created)"})
        .values("month")
        .annotate(count=Count("id"))
        .order_by("month")
    )

    monthly_bids = (
        Bid.objects.filter(created_at__gte=six_months_ago)
        .extra(select={"month": "strftime('%%Y-%%m', created_at)"})
        .values("month")
        .annotate(count=Count("id"), total_amount=Sum("amount"))
        .order_by("month")
    )

    # Top bidders
    top_bidders = (
        User.objects.annotate(
            bid_count=Count("bids"), total_bid_amount=Sum("bids__amount")
        )
        .filter(bid_count__gt=0)
        .order_by("-total_bid_amount")[:5]
    )

    # Most popular listings (by bid count)
    popular_listings = (
        Listing.objects.annotate(bid_count=Count("bids"))
        .filter(bid_count__gt=0)
        .order_by("-bid_count")[:5]
    )

    context = {
        # General KPIs
        "total_listings": total_listings,
        "active_listings": active_listings,
        "total_users": total_users,
        "total_bids": total_bids,
        # User KPIs
        "user_active_listings": user_active_listings,
        "user_total_listings": user_total_listings,
        "user_bids": user_bids,
        # Financial KPIs
        "total_bid_amount": total_bid_amount,
        "avg_bid_amount": avg_bid_amount,
        # Analytics data for charts
        "category_stats": list(category_stats),
        "monthly_listings": list(monthly_listings),
        "monthly_bids": list(monthly_bids),
        "top_bidders": top_bidders,
        "popular_listings": popular_listings,
        # Recent activity
        "recent_listings": recent_listings,
        "recent_bids": recent_bids,
    }

    return render(request, "auctions/dashboard.html", context)


# Rate limiting is now handled by custom decorator above
