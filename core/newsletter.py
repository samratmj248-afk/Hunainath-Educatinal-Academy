"""
Newsletter email delivery helpers for Shree Hunainath Educational Academy.
"""

from django.conf import settings
from django.core.mail import EmailMultiAlternatives, get_connection
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone
from django.utils.html import strip_tags

from .models import Newsletter, NewsletterSubscriber, SchoolProfile


def _site_url(request=None):
    if request is not None:
        return request.build_absolute_uri("/").rstrip("/")
    return getattr(settings, "SITE_URL", "http://127.0.0.1:8000").rstrip("/")


def send_newsletter(newsletter: Newsletter, request=None, recipients=None):
    """
    Email a newsletter to all active subscribers (or the given subscriber queryset).
    Each email is personalised with its own unsubscribe link.
    Returns the number of emails sent.
    """
    subscribers = recipients if recipients is not None else NewsletterSubscriber.objects.filter(is_active=True)
    school = SchoolProfile.objects.first()
    base_url = _site_url(request)
    cover_url = f"{base_url}{newsletter.cover_image.url}" if newsletter.cover_image else ""

    connection = get_connection()
    messages = []
    for sub in subscribers:
        unsubscribe_url = base_url + reverse("newsletter_unsubscribe", args=[sub.unsubscribe_token])
        ctx = {
            "newsletter": newsletter,
            "subscriber": sub,
            "school": school,
            "site_url": base_url,
            "cover_url": cover_url,
            "unsubscribe_url": unsubscribe_url,
        }
        html = render_to_string("emails/newsletter.html", ctx)
        msg = EmailMultiAlternatives(
            subject=newsletter.subject,
            body=strip_tags(html),
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[sub.email],
            connection=connection,
            headers={"List-Unsubscribe": f"<{unsubscribe_url}>"},
        )
        msg.attach_alternative(html, "text/html")
        messages.append(msg)

    sent = connection.send_messages(messages) if messages else 0

    if recipients is None:
        newsletter.status = "SENT"
        newsletter.sent_at = timezone.now()
        newsletter.recipients_count = sent or 0
        newsletter.save(update_fields=["status", "sent_at", "recipients_count"])
    return sent or 0
