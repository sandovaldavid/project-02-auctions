from django import template
from auctions.models import Watchlist
from decimal import Decimal
import json

register = template.Library()


@register.filter
def multiply(value, arg):
    """Multiplies the value by the argument"""
    try:
        return int(value) * int(arg)
    except (ValueError, TypeError):
        return value


@register.filter
def is_in_watchlist(listing, user):
    """Check if a listing is in user's watchlist"""
    if not user.is_authenticated:
        return False
    return Watchlist.objects.filter(user=user, listing=listing, active=True).exists()


@register.filter
def to_json(value):
    """Convert Python data to JSON, handling Decimal types"""

    def decimal_handler(obj):
        if isinstance(obj, Decimal):
            return float(obj)
        raise TypeError

    return json.dumps(value, default=decimal_handler)
