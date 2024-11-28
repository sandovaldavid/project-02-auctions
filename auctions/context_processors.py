from .models import Watchlist

def watchlist_count(request):
    if request.user.is_authenticated:
        watchlist_count = Watchlist.objects.filter(user=request.user, active=True).count()
    else:
        watchlist_count = 0
    return {'watchlist_count': watchlist_count}
