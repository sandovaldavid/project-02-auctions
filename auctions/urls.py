from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("addAuctions", views.new_auctions, name="addAuctions"),
    path("listing/<int:listing_id>", views.listing, name="listing"),
    path("bid/<int:listing_id>", views.bid, name="bid"),
    path("watchlist/<int:listing_id>", views.watchlist, name="watchlist"),
    path("my-watchlist", views.my_watchlist, name="my_watchlist"),
    # skipcq: FLK-E501
    path(
        "Watchlist_remove/<int:listing_id>",
        views.watchlist_remove,
        name="watchlist_remove",
    ),
    path("listing/<int:listing_id>/close", views.close_auction, name="close_auction"),
    path("categories", views.categories, name="categories"),
    path("search", views.search, name="search"),
    path("search/autocomplete", views.search_autocomplete, name="search_autocomplete"),
    path("comment/<int:listing_id>", views.comment, name="comment"),
    path("notifications", views.notifications, name="notifications"),
    path("profile", views.profile, name="profile"),
    path("dashboard", views.dashboard, name="dashboard"),
]
