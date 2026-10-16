"""
URL routes for core application of Shree Hunainath Educational Academy.
"""

from django.urls import path
from . import views

urlpatterns = [
    # Public Academy Pages
    path("", views.index, name="index"),
    path("about/", views.about, name="about"),
    path("programs/", views.programs_list, name="programs"),
    path("programs/<slug:slug>/", views.program_detail, name="program_detail"),
    path("academics/", views.academics_hub, name="academics_hub"),
    path("academics/routines/", views.exam_routines, name="exam_routines"),
    path("academics/results/", views.exam_results, name="exam_results"),
    path("blog/", views.blog_list, name="blog_list"),
    path("blog/<slug:slug>/", views.blog_detail, name="blog_detail"),
    path("admissions/", views.admissions, name="admissions"),
    path("admissions/status/", views.check_admission_status, name="admission_status"),
    path("notices/", views.notices_list, name="notices"),
    path("notices/<slug:slug>/", views.notice_detail, name="notice_detail"),
    path("gallery/", views.gallery, name="gallery"),
    path("faculty/", views.faculty, name="faculty"),
    path("contact/", views.contact, name="contact"),
    path("faq/", views.faq, name="faq"),
    path("terms-and-conditions/", views.terms_and_conditions, name="terms_and_conditions"),

    # PWA Endpoints
    path("sw.js", views.service_worker, name="service_worker"),
    path("manifest.json", views.manifest, name="manifest_json"),
    path("site.webmanifest", views.manifest, name="site_webmanifest"),
    path("offline/", views.offline, name="offline"),

    # Web Push API
    path("api/push/vapid-key/", views.vapid_public_key, name="push_vapid_key"),
    path("api/push/subscribe/", views.push_subscribe, name="push_subscribe"),
    path("api/push/unsubscribe/", views.push_unsubscribe, name="push_unsubscribe"),

    # SEO & Search Engine Crawlers
    path("robots.txt", views.robots_txt, name="robots_txt"),
    path("sitemap.xml", views.sitemap_xml, name="sitemap_xml"),
]
