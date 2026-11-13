"""
Global context processors for Shree Hunainath Educational Academy.
Supplies school brand data, urgent notices ticker, and push configs across all templates.
"""

from datetime import datetime
from django.conf import settings

def school_settings(request):
    """
    Exposes singleton school profile, urgent tickers, and VAPID key.
    Uses request-level caching to avoid duplicate database hits across views and context processors.
    """
    from core.models import SchoolProfile, Notice

    profile = getattr(request, "_cached_school_profile", None)
    if profile is None:
        try:
            profile = SchoolProfile.objects.first()
            request._cached_school_profile = profile
        except Exception:
            profile = None

    # Ticker notices for top news bar
    try:
        urgent_tickers = Notice.objects.filter(is_active=True, is_ticker=True).order_by("-published_at")[:5]
    except Exception:
        urgent_tickers = []

    return {
        "school": profile,
        "urgent_tickers": urgent_tickers,
        "vapid_public_key": getattr(settings, "VAPID_PUBLIC_KEY", ""),
        "current_year": datetime.now().year,
    }
