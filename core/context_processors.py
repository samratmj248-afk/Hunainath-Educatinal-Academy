"""
Global context processors for Shree Hunainath Educational Academy.
Supplies school brand data, urgent notices ticker, and push configs across all templates.
"""

from datetime import datetime
from django.conf import settings

def school_settings(request):
    """
    Exposes singleton school profile, urgent tickers, and VAPID key.
    """
    from core.models import SchoolProfile, Notice

    profile = None
    try:
        profile = SchoolProfile.objects.first()
    except Exception:
        profile = None

    # Ticker notices for top news bar
    try:
        urgent_tickers = Notice.objects.filter(is_active=True, is_ticker=True).order_by("-published_at")[:5]
    except Exception:
        urgent_tickers = []

    # Recent notices for footer/sidebar
    try:
        recent_notices = Notice.objects.filter(is_active=True).order_by("-published_at")[:4]
    except Exception:
        recent_notices = []

    # Footer gallery photos
    try:
        from core.models import GalleryItem
        footer_gallery_items = GalleryItem.objects.filter(is_featured=True).order_by("order")[:6]
    except Exception:
        footer_gallery_items = []

    return {
        "school": profile,
        "urgent_tickers": urgent_tickers,
        "recent_notices": recent_notices,
        "footer_gallery_items": footer_gallery_items,
        "vapid_public_key": getattr(settings, "VAPID_PUBLIC_KEY", ""),
        "current_year": datetime.now().year,
    }
