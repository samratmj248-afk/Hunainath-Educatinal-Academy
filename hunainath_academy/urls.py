"""
URL Configuration for hunainath_academy project.
"""

from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve

from core import views as core_views

urlpatterns = [
    path("admin/app-qr-standee/", core_views.admin_qr_standee, name="admin_qr_standee"),
    path("admin/app-qr-code.png", core_views.admin_qr_download, name="admin_qr_download"),
    path("admin/", admin.site.urls),
    path("", include("core.urls")),
    re_path(r"^media/(?P<path>.*)$", serve, {"document_root": settings.MEDIA_ROOT}),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

handler404 = "core.views_errors.custom_page_not_found"
handler500 = "core.views_errors.custom_server_error"
handler403 = "core.views_errors.custom_permission_denied"
