"""
Custom Fortune-500 Error Handlers with Academy UI.
"""

from django.shortcuts import render
from core.models import SchoolProfile


def get_profile():
    return SchoolProfile.objects.first()


def custom_page_not_found(request, exception=None):
    school = get_profile()
    return render(
        request,
        "errors/404.html",
        {"school": school, "page_title": "Page Not Found (404)"},
        status=404,
    )


def custom_server_error(request):
    school = get_profile()
    return render(
        request,
        "errors/500.html",
        {"school": school, "page_title": "Internal Server Error (500)"},
        status=500,
    )


def custom_permission_denied(request, exception=None):
    school = get_profile()
    return render(
        request,
        "errors/403.html",
        {"school": school, "page_title": "Access Denied (403)"},
        status=403,
    )
