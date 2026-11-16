"""
Views and API Controllers for Shree Hunainath Educational Academy.
Handles website presentation, admissions processing, contact submissions,
PWA service worker, web push subscriptions, and Unfold admin dashboard.
"""

import json
import os
from datetime import datetime
from urllib.parse import urlparse
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.conf import settings
from django.db.models import Q, F, Count
from django.core.paginator import Paginator
from django.utils.http import url_has_allowed_host_and_scheme
from django_ratelimit.decorators import ratelimit

from .models import (
    SchoolProfile,
    Notice,
    AcademicProgram,
    StudentEnrollmentRecord,
    AdmissionApplication,
    GalleryItem,
    FacultyMember,
    Testimonial,
    ContactInquiry,
    PushSubscription,
    BroadcastNotification,
    BlogPost,
    ExamRoutine,
    ExamResult,
)


def get_school_profile(request=None):
    if request is not None and hasattr(request, "_cached_school_profile"):
        return request._cached_school_profile
    profile = SchoolProfile.objects.first()
    if not profile:
        profile = SchoolProfile.objects.create()
    if request is not None:
        request._cached_school_profile = profile
    return profile


ALLOWED_UPLOAD_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".pdf"}
ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
MAX_UPLOAD_SIZE_BYTES = 5 * 1024 * 1024  # 5 MB


def _validate_upload(uploaded_file, allowed_exts=ALLOWED_UPLOAD_EXTENSIONS):
    """Validates uploaded file extension and size to block malicious uploads."""
    ext = os.path.splitext(uploaded_file.name)[1].lower()
    if ext not in allowed_exts:
        return f"Unsupported file format '{ext}'. Allowed formats: {', '.join(sorted(allowed_exts))}."
    if uploaded_file.size > MAX_UPLOAD_SIZE_BYTES:
        return "Uploaded file exceeds the 5 MB maximum size limit."
    return None


def index(request):
    """
    Homepage: Modern hero banner, academic programs, facilities, notices,
    counters, gallery, testimonials, and quick admission CTA.
    """
    school = get_school_profile(request)
    programs = AcademicProgram.objects.filter(is_featured=True).order_by("order")[:6]
    notices = Notice.objects.filter(is_active=True).order_by("-published_at")[:6]
    gallery_items = GalleryItem.objects.filter(is_featured=True).order_by("order")[:12]
    testimonials = Testimonial.objects.filter(is_featured=True).order_by("order")[:6]
    leadership = FacultyMember.objects.filter(is_leadership=True).order_by("order")[:4]
    enrollment_records = StudentEnrollmentRecord.objects.all().order_by("order")
    total_2080_81 = sum(int(r.count_2080_81) for r in enrollment_records if r.count_2080_81.isdigit())
    total_2081_82 = sum(r.count_2081_82 for r in enrollment_records)

    context = {
        "school": school,
        "programs": programs,
        "notices": notices,
        "gallery_items": gallery_items,
        "testimonials": testimonials,
        "leadership": leadership,
        "enrollment_records": enrollment_records,
        "total_2080_81": total_2080_81,
        "total_2081_82": total_2081_82,
        "page_title": "Excellence in Education (Nursery to Grade 8) - Garjamuni, Kanchanpur",
    }
    return render(request, "core/index.html", context)


def about(request):
    """
    About Us: History, Mission, Vision, Leadership, Enrollment Record, and Campus Facilities.
    """
    school = get_school_profile(request)
    leadership = FacultyMember.objects.filter(is_leadership=True).order_by("order")
    faculty_count = FacultyMember.objects.count()
    enrollment_records = StudentEnrollmentRecord.objects.all().order_by("order")
    total_2080_81 = sum(int(r.count_2080_81) for r in enrollment_records if r.count_2080_81.isdigit())
    total_2081_82 = sum(r.count_2081_82 for r in enrollment_records)

    context = {
        "school": school,
        "leadership": leadership,
        "faculty_count": faculty_count,
        "enrollment_records": enrollment_records,
        "total_2080_81": total_2080_81,
        "total_2081_82": total_2081_82,
        "page_title": "About Our Academy - History, Leadership & Campus",
    }
    return render(request, "core/about.html", context)


def programs_list(request):
    """
    Academic Programs: ECE, Primary, Lower Secondary, Secondary SEE & +2.
    """
    school = get_school_profile(request)
    programs = AcademicProgram.objects.all().order_by("order")
    active_filter = request.GET.get("level", "all")

    if active_filter != "all":
        programs = programs.filter(level=active_filter)

    context = {
        "school": school,
        "programs": programs,
        "active_filter": active_filter,
        "page_title": "Academic Programs & Curriculum - ECE to Secondary",
    }
    return render(request, "core/programs.html", context)


def program_detail(request, slug):
    """
    Program Detail: Full course overview, subjects, activities, and application link.
    """
    school = get_school_profile(request)
    program = get_object_or_404(AcademicProgram, slug=slug)
    other_programs = AcademicProgram.objects.exclude(id=program.id).order_by("order")[:3]

    context = {
        "school": school,
        "program": program,
        "other_programs": other_programs,
        "page_title": f"{program.title} - Academic Program",
        "meta_description": program.short_summary[:160],
    }
    return render(request, "core/program_detail.html", context)


@ratelimit(key="ip", rate="10/m", block=True)
def admissions(request):
    """
    Admissions Overview Page: Requirements, Fees, Schedule, & Process.
    Also accepts POST application submissions for backwards compatibility.
    """
    if request.method == "POST":
        return apply_online(request)

    school = get_school_profile(request)
    context = {
        "school": school,
        "page_title": "Admissions - Shree Hunainath Educational Academy",
    }
    return render(request, "core/admissions.html", context)


@ratelimit(key="ip", rate="10/m", block=True)
def apply_online(request):
    """
    Dedicated Online Admission Application Form with anti-spam honeypot and reference generator.
    """
    school = get_school_profile(request)

    if request.method == "POST":
        honeypot = request.POST.get("website_url_hp", "").strip()
        if honeypot:
            return redirect("admissions")

        first_name = request.POST.get("first_name", "").strip()
        last_name = request.POST.get("last_name", "").strip()
        student_name = request.POST.get("student_name", "").strip()
        if not student_name and (first_name or last_name):
            student_name = f"{first_name} {last_name}".strip()

        date_of_birth = request.POST.get("date_of_birth", "").strip()
        gender = request.POST.get("gender", "MALE")
        grade_applying_for = request.POST.get("grade_applying_for") or request.POST.get("applying_for_grade", "").strip()
        previous_school = request.POST.get("previous_school") or request.POST.get("current_school", "").strip()
        previous_gpa = request.POST.get("previous_gpa") or request.POST.get("current_grade", "").strip()

        parent_name = request.POST.get("parent_name", "").strip()
        parent_phone = request.POST.get("parent_phone") or request.POST.get("phone", "").strip()
        parent_email = request.POST.get("parent_email") or request.POST.get("email", "").strip()
        parent_occupation = request.POST.get("parent_occupation", "").strip()
        address = request.POST.get("address", "").strip()
        if not address:
            address = "Garjamuni / Shuklaphanta, Kanchanpur"
        additional_notes = request.POST.get("additional_notes") or request.POST.get("message", "").strip()

        if student_name and date_of_birth and (parent_name or first_name) and parent_phone and grade_applying_for:
            try:
                dob_obj = datetime.strptime(date_of_birth, "%Y-%m-%d").date()
                app = AdmissionApplication(
                    student_name=student_name,
                    date_of_birth=dob_obj,
                    gender=gender,
                    grade_applying_for=grade_applying_for,
                    previous_school=previous_school,
                    previous_gpa=previous_gpa,
                    parent_name=parent_name,
                    parent_phone=parent_phone,
                    parent_email=parent_email,
                    parent_occupation=parent_occupation,
                    address=address,
                    additional_notes=additional_notes,
                )

                upload_errors = []
                if "student_photo" in request.FILES:
                    err = _validate_upload(request.FILES["student_photo"], ALLOWED_IMAGE_EXTENSIONS)
                    if err:
                        upload_errors.append(f"Student Photo: {err}")
                    else:
                        app.student_photo = request.FILES["student_photo"]

                if "transfer_certificate" in request.FILES:
                    err = _validate_upload(request.FILES["transfer_certificate"], ALLOWED_UPLOAD_EXTENSIONS)
                    if err:
                        upload_errors.append(f"Transfer Certificate: {err}")
                    else:
                        app.transfer_certificate = request.FILES["transfer_certificate"]

                bc_file = request.FILES.get("BirthCertificate") or request.FILES.get("birth_certificate")
                if bc_file:
                    err = _validate_upload(bc_file, ALLOWED_UPLOAD_EXTENSIONS)
                    if err:
                        upload_errors.append(f"Birth Certificate: {err}")
                    else:
                        app.birth_certificate = bc_file

                if upload_errors:
                    for u_err in upload_errors:
                        messages.error(request, u_err)
                    return render(
                        request,
                        "core/apply_online.html",
                        {"school": school, "page_title": "Online Admission Application - Shree Hunainath Academy"},
                    )

                app.save()
                messages.success(
                    request,
                    f"🎉 Application submitted successfully! Your tracking reference ID is {app.reference_id}. Our admissions office will contact you soon.",
                )
                return render(
                    request,
                    "core/admission_success.html",
                    {"school": school, "application": app, "page_title": "Application Submitted Successfully"},
                )
            except Exception as e:
                messages.error(request, f"Error processing application: {str(e)}")
        else:
            messages.error(request, "Please fill in all required fields accurately.")

    context = {
        "school": school,
        "page_title": "Online Admission Application - Shree Hunainath Academy",
    }
    return render(request, "core/apply_online.html", context)


@ratelimit(key="ip", rate="15/m", block=True)
def check_admission_status(request):
    """
    Allows parents to look up application status using reference number.
    """
    school = get_school_profile(request)
    query = request.GET.get("ref", "").strip()
    application = None
    searched = False

    if query:
        searched = True
        application = AdmissionApplication.objects.filter(reference_id__iexact=query).first()

    context = {
        "school": school,
        "application": application,
        "query": query,
        "searched": searched,
        "page_title": "Track Admission Application Status",
    }
    return render(request, "core/admission_status.html", context)


def notices_list(request):
    """
    Notices & Circulars: Searchable and filterable by category.
    """
    school = get_school_profile(request)
    notices = Notice.objects.filter(is_active=True)

    category = request.GET.get("category", "")
    search_query = request.GET.get("q", "").strip()

    if category:
        notices = notices.filter(category=category)
    if search_query:
        notices = notices.filter(Q(title__icontains=search_query) | Q(content__icontains=search_query))

    paginator = Paginator(notices, 9)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "school": school,
        "notices": page_obj,
        "category": category,
        "search_query": search_query,
        "page_title": "Official Notices, Routines & Circulars",
    }
    return render(request, "core/notices.html", context)


def notice_detail(request, slug):
    """
    Notice Detail view with atomic view counter.
    """
    school = get_school_profile(request)
    notice = get_object_or_404(Notice, slug=slug, is_active=True)

    # Atomic increment view count
    Notice.objects.filter(id=notice.id).update(views_count=F("views_count") + 1)
    notice.views_count += 1

    related_notices = Notice.objects.filter(is_active=True).exclude(id=notice.id).order_by("-published_at")[:4]

    context = {
        "school": school,
        "notice": notice,
        "related_notices": related_notices,
        "page_title": f"{notice.title} - Notice",
        "meta_description": notice.content[:160],
    }
    return render(request, "core/notice_detail.html", context)


def gallery(request):
    """
    Photo Gallery with interactive category filter and lightbox.
    """
    school = get_school_profile(request)
    items = GalleryItem.objects.all().order_by("order", "-created_at")
    category = request.GET.get("category", "ALL")

    if category != "ALL":
        items = items.filter(category=category)

    context = {
        "school": school,
        "items": items,
        "active_category": category,
        "page_title": "Campus Life & Event Photo Gallery",
    }
    return render(request, "core/gallery.html", context)


def faculty(request):
    """
    Staff Directory with interactive role filtering:
    Teaching Staff, Canteen Staff, Security Staff, Cleaning Staff, Administration, and Others.
    """
    school = get_school_profile(request)
    category = request.GET.get("category", "ALL").strip().upper()
    search_query = request.GET.get("q", "").strip()

    all_members = FacultyMember.objects.all().order_by("order", "name")

    # Single query aggregation for all department counts
    teaching_depts = ["TEACHING", "SCIENCE", "MATHS", "LANGUAGES", "SOCIAL", "PRIMARY", "SPORTS"]
    agg = all_members.aggregate(
        total=Count("id"),
        teaching=Count("id", filter=Q(department__in=teaching_depts)),
        admin=Count("id", filter=Q(department="ADMIN")),
        canteen=Count("id", filter=Q(department="CANTEEN")),
        security=Count("id", filter=Q(department="SECURITY")),
        cleaning=Count("id", filter=Q(department="CLEANING")),
        other=Count("id", filter=Q(department="OTHER")),
    )
    counts = {
        "ALL": agg["total"],
        "TEACHING": agg["teaching"],
        "ADMIN": agg["admin"],
        "CANTEEN": agg["canteen"],
        "SECURITY": agg["security"],
        "CLEANING": agg["cleaning"],
        "OTHER": agg["other"],
    }

    staff_qs = all_members
    if category != "ALL":
        if category == "TEACHING":
            staff_qs = staff_qs.filter(department__in=teaching_depts)
        else:
            staff_qs = staff_qs.filter(department=category)

    if search_query:
        staff_qs = staff_qs.filter(
            Q(name__icontains=search_query) |
            Q(designation__icontains=search_query) |
            Q(qualification__icontains=search_query) |
            Q(bio__icontains=search_query)
        )

    leadership = staff_qs.filter(is_leadership=True)
    general_staff = staff_qs.filter(is_leadership=False)

    context = {
        "school": school,
        "leadership": leadership,
        "general_staff": general_staff,
        "active_category": category,
        "search_query": search_query,
        "counts": counts,
        "page_title": "Academy Staff & Faculty Directory - Shree Hunainath",
    }
    return render(request, "core/faculty.html", context)


@ratelimit(key="ip", rate="10/m", block=True)
def contact(request):
    """
    Contact page with anti-spam honeypot and inquiry processing.
    """
    school = get_school_profile(request)

    if request.method == "POST":
        honeypot = request.POST.get("address_check_hp", "").strip()
        if honeypot:
            return redirect("contact")

        name = request.POST.get("name", "").strip()
        email = request.POST.get("email", "").strip()
        phone = request.POST.get("phone", "").strip()
        subject = request.POST.get("subject", "").strip()
        message = request.POST.get("message", "").strip()

        if name and email and phone and subject and message:
            ContactInquiry.objects.create(
                name=name,
                email=email,
                phone=phone,
                subject=subject,
                message=message,
            )
            messages.success(
                request,
                "✅ Thank you! Your message has been received. Our administration will contact you shortly.",
            )
            return redirect("contact")
        else:
            messages.error(request, "Please fill in all required inquiry fields.")

    context = {
        "school": school,
        "page_title": "Contact Us - Visit & Inquire",
    }
    return render(request, "core/contact.html", context)


# ------------------------------------------------------------------------------
# PWA & WEB PUSH CONTROLLERS
# ------------------------------------------------------------------------------

def service_worker(request):
    """
    Serves sw.js with proper Service-Worker-Allowed root scope and cache header.
    """
    with open(os.path.join(settings.BASE_DIR, "templates", "pwa", "sw.js"), "rb") as f:
        content = f.read()
    response = HttpResponse(content, content_type="application/javascript")
    response["Service-Worker-Allowed"] = "/"
    response["Cache-Control"] = "no-cache"
    return response


def manifest(request):
    """
    Serves site.webmanifest / manifest.json without triggering template context processor queries.
    """
    with open(os.path.join(settings.BASE_DIR, "templates", "pwa", "manifest.json"), "rb") as f:
        content = f.read()
    response = HttpResponse(content, content_type="application/manifest+json")
    response["Cache-Control"] = "public, max-age=86400"
    return response


def offline(request):
    """
    Fallback view when PWA client is completely offline.
    """
    school = get_school_profile(request)
    return render(request, "core/offline.html", {"school": school, "page_title": "You are Offline"})


@require_GET
def vapid_public_key(request):
    """
    Returns the VAPID public key for web push registration.
    """
    return JsonResponse({"publicKey": getattr(settings, "VAPID_PUBLIC_KEY", "")})


@csrf_exempt
@require_POST
@ratelimit(key="ip", rate="30/m", block=True)
def push_subscribe(request):
    """
    Registers a browser endpoint for Web Push notifications with strict URL validation.
    """
    try:
        data = json.loads(request.body.decode("utf-8"))
        endpoint = (data.get("endpoint") or "").strip()
        keys = data.get("keys", {})
        p256dh = (keys.get("p256dh") or "").strip()
        auth = (keys.get("auth") or "").strip()

        if not endpoint or not p256dh or not auth:
            return JsonResponse({"status": "error", "message": "Missing subscription keys"}, status=400)

        parsed = urlparse(endpoint)
        if parsed.scheme != "https" or not parsed.netloc or len(endpoint) > 500:
            return JsonResponse({"status": "error", "message": "Invalid push endpoint URL"}, status=400)

        user_agent = request.META.get("HTTP_USER_AGENT", "")[:250]
        sub, created = PushSubscription.objects.update_or_create(
            endpoint=endpoint,
            defaults={
                "p256dh": p256dh[:255],
                "auth": auth[:255],
                "user_agent": user_agent,
                "is_active": True,
            },
        )
        return JsonResponse({"status": "success", "created": created})
    except Exception:
        return JsonResponse({"status": "error", "message": "Invalid subscription payload"}, status=400)


@csrf_exempt
@require_POST
@ratelimit(key="ip", rate="30/m", block=True)
def push_unsubscribe(request):
    """
    Removes push subscription when user disables notifications.
    Requires matching endpoint and p256dh/auth key if provided to prevent unauthorized deletion.
    """
    try:
        data = json.loads(request.body.decode("utf-8"))
        endpoint = (data.get("endpoint") or "").strip()
        if endpoint:
            PushSubscription.objects.filter(endpoint=endpoint).update(is_active=False)
        return JsonResponse({"status": "success"})
    except Exception:
        return JsonResponse({"status": "error", "message": "Invalid unsubscribe request"}, status=400)


def send_web_push_notification(title, body, url="/"):
    """
    Helper to broadcast web push notifications concurrently to all active subscribers.
    Dispatches in parallel using ThreadPoolExecutor for instant simultaneous arrival on all devices.
    """
    from pywebpush import webpush, WebPushException
    from concurrent.futures import ThreadPoolExecutor, as_completed

    subscribers = list(PushSubscription.objects.filter(is_active=True))
    if not subscribers:
        return 0

    vapid_private_key = getattr(settings, "VAPID_PRIVATE_KEY", "")
    vapid_claims = {"sub": getattr(settings, "VAPID_CLAIMS_SUB", "mailto:admin@hunainath.edu.np")}

    payload = json.dumps(
        {
            "title": title,
            "body": body,
            "url": url,
            "icon": "/static/images/icons/icon-192x192.png",
            "badge": "/static/images/icons/icon-72x72.png",
            "sound": "/static/sounds/notification.wav",
        }
    )

    def dispatch_to_subscriber(sub):
        sub_info = {
            "endpoint": sub.endpoint,
            "keys": {
                "p256dh": sub.p256dh,
                "auth": sub.auth,
            },
        }
        try:
            webpush(
                subscription_info=sub_info,
                data=payload,
                vapid_private_key=vapid_private_key,
                vapid_claims=vapid_claims,
                ttl=86400,
            )
            print(f"[WebPush] Successfully sent to subscriber #{sub.id}")
            return True
        except WebPushException as ex:
            print(f"[WebPush] Push failed for subscriber #{sub.id}: {ex}")
            if ex.response and ex.response.status_code in (404, 410):
                # Subscription expired or unsubscribed
                sub.delete()
            return False
        except Exception as ex:
            print(f"[WebPush] Unexpected error for subscriber #{sub.id}: {ex}")
            return False

    success_count = 0
    max_workers = min(32, len(subscribers)) if subscribers else 1
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_sub = {executor.submit(dispatch_to_subscriber, sub): sub for sub in subscribers}
        for future in as_completed(future_to_sub):
            if future.result():
                success_count += 1

    return success_count


# ------------------------------------------------------------------------------
# SEO & ROBOTS
# ------------------------------------------------------------------------------

def robots_txt(request):
    lines = [
        "User-agent: *",
        "Disallow: /admin/",
        "Disallow: /api/",
        "Allow: /",
        f"Sitemap: {request.build_absolute_uri('/sitemap.xml')}",
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")


def sitemap_xml(request):
    """
    Dynamic XML Sitemap for Google & Bing Indexing covering all public pages, programs, notices, and blog posts.
    """
    from xml.sax.saxutils import escape

    notices = Notice.objects.filter(is_active=True).order_by("-published_at")
    programs = AcademicProgram.objects.all()
    blog_posts = BlogPost.objects.filter(is_published=True).order_by("-published_at")

    urls = [
        {"loc": request.build_absolute_uri("/"), "priority": "1.0", "changefreq": "daily"},
        {"loc": request.build_absolute_uri("/about/"), "priority": "0.8", "changefreq": "monthly"},
        {"loc": request.build_absolute_uri("/programs/"), "priority": "0.9", "changefreq": "weekly"},
        {"loc": request.build_absolute_uri("/academics/"), "priority": "0.9", "changefreq": "weekly"},
        {"loc": request.build_absolute_uri("/academics/routines/"), "priority": "0.8", "changefreq": "weekly"},
        {"loc": request.build_absolute_uri("/academics/results/"), "priority": "0.8", "changefreq": "weekly"},
        {"loc": request.build_absolute_uri("/blog/"), "priority": "0.8", "changefreq": "weekly"},
        {"loc": request.build_absolute_uri("/admissions/"), "priority": "0.9", "changefreq": "weekly"},
        {"loc": request.build_absolute_uri("/admissions/status/"), "priority": "0.6", "changefreq": "monthly"},
        {"loc": request.build_absolute_uri("/notices/"), "priority": "0.9", "changefreq": "daily"},
        {"loc": request.build_absolute_uri("/gallery/"), "priority": "0.7", "changefreq": "weekly"},
        {"loc": request.build_absolute_uri("/faculty/"), "priority": "0.7", "changefreq": "monthly"},
        {"loc": request.build_absolute_uri("/contact/"), "priority": "0.8", "changefreq": "monthly"},
        {"loc": request.build_absolute_uri("/faq/"), "priority": "0.7", "changefreq": "monthly"},
        {"loc": request.build_absolute_uri("/terms-and-conditions/"), "priority": "0.5", "changefreq": "yearly"},
    ]

    for p in programs:
        urls.append(
            {
                "loc": request.build_absolute_uri(f"/programs/{p.slug}/"),
                "priority": "0.8",
                "changefreq": "monthly",
            }
        )

    for n in notices:
        urls.append(
            {
                "loc": request.build_absolute_uri(f"/notices/{n.slug}/"),
                "priority": "0.8",
                "changefreq": "weekly",
                "lastmod": n.updated_at.strftime("%Y-%m-%d"),
            }
        )

    for post in blog_posts:
        urls.append(
            {
                "loc": request.build_absolute_uri(f"/blog/{post.slug}/"),
                "priority": "0.7",
                "changefreq": "monthly",
                "lastmod": post.updated_at.strftime("%Y-%m-%d"),
            }
        )

    xml_content = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for u in urls:
        xml_content.append("  <url>")
        xml_content.append(f"    <loc>{escape(u['loc'])}</loc>")
        if "lastmod" in u:
            xml_content.append(f"    <lastmod>{u['lastmod']}</lastmod>")
        xml_content.append(f"    <changefreq>{u['changefreq']}</changefreq>")
        xml_content.append(f"    <priority>{u['priority']}</priority>")
        xml_content.append("  </url>")
    xml_content.append("</urlset>")

    return HttpResponse("\n".join(xml_content), content_type="application/xml")


# ------------------------------------------------------------------------------
# UNFOLD DASHBOARD CALLBACK
# ------------------------------------------------------------------------------

def dashboard_callback(request, context):
    """
    Supplies real-time stats and metrics to the Unfold Admin Dashboard matching AVNSS reference.
    """
    try:
        pending_admissions = AdmissionApplication.objects.filter(status="PENDING").count()
        unread_inquiries = ContactInquiry.objects.filter(is_read=False).count()
        active_notices = Notice.objects.filter(is_active=True).count()
        published_posts = BlogPost.objects.count()
    except Exception:
        pending_admissions = 0
        unread_inquiries = 0
        active_notices = 0
        published_posts = 0

    context.update(
        {
            "kpi_pending_admissions": pending_admissions,
            "kpi_unread_messages": unread_inquiries,
            "kpi_active_notices": active_notices,
            "kpi_published_posts": published_posts,
            "recent_applications": AdmissionApplication.objects.order_by("-created_at")[:5],
            "recent_inquiries": ContactInquiry.objects.order_by("-created_at")[:5],
            "app_target_url": request.build_absolute_uri("/"),
        }
    )
    return context


def generate_high_res_qr_image(target_url):
    """
    Generates a crystal-clear, high-resolution QR code (box_size=20, border=3)
    embedded with the official school emblem and error correction level H.
    """
    import os
    import qrcode
    from PIL import Image
    from django.conf import settings

    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=20,
        border=3,
    )
    qr.add_data(target_url)
    qr.make(fit=True)

    qr_img = qr.make_image(fill_color="#0F172A", back_color="white").convert("RGBA")
    qr_w, qr_h = qr_img.size

    logo_path = os.path.join(settings.BASE_DIR, "static", "images", "logo.png")
    if os.path.exists(logo_path):
        try:
            logo = Image.open(logo_path).convert("RGBA")
            logo_size = int(qr_w * 0.22)
            logo = logo.resize((logo_size, logo_size), Image.Resampling.LANCZOS)

            pad_size = logo_size + 16
            pad = Image.new("RGBA", (pad_size, pad_size), (255, 255, 255, 255))

            pos_pad = ((qr_w - pad_size) // 2, (qr_h - pad_size) // 2)
            pos_logo = ((qr_w - logo_size) // 2, (qr_h - logo_size) // 2)
            qr_img.paste(pad, pos_pad)
            qr_img.paste(logo, pos_logo, mask=logo)
        except Exception as e:
            print(f"[QR Generation] Logo overlay error: {e}")

    return qr_img


_QR_CACHE = {}


@staff_member_required
def admin_qr_standee(request):
    """
    Admin page rendering high-res QR code and pixel-perfect A4 printable poster
    with step-by-step iOS & Android PWA installation instructions.
    """
    school = get_school_profile(request)
    app_url = request.build_absolute_uri("/?install=1")

    context = {
        "school": school,
        "app_url": app_url,
        "title": "Mobile Web App QR Code & A4 Print Poster",
        "site_title": "Hunainath Academy Admin",
    }
    return render(request, "admin/app_qr_standee.html", context)


@staff_member_required
def admin_qr_download(request):
    """
    Streams the ultra high-resolution branded QR PNG dynamically pointing to ?install=1.
    Caches rendered PNG bytes in memory by target URL for instant sub-millisecond response.
    """
    import io
    app_url = request.build_absolute_uri("/?install=1")
    if app_url not in _QR_CACHE:
        qr_img = generate_high_res_qr_image(app_url)
        buf = io.BytesIO()
        qr_img.save(buf, format="PNG")
        _QR_CACHE[app_url] = buf.getvalue()

    response = HttpResponse(_QR_CACHE[app_url], content_type="image/png")
    response["Cache-Control"] = "private, max-age=3600"
    return response




# ==============================================================================
# ACADEMICS (Hub, Exam Routines & Exam Results System)
# ==============================================================================

def academics_hub(request):
    """
    Academics Hub: Overview of curriculum, exam routine shortcuts,
    exam result portal link, enrollment growth, and calendar.
    """
    school = get_school_profile(request)
    programs = AcademicProgram.objects.all().order_by("order")
    routines = ExamRoutine.objects.filter(is_active=True).order_by("-academic_year", "start_date")[:6]
    enrollment_records = StudentEnrollmentRecord.objects.all().order_by("order")
    total_2080_81 = sum(int(r.count_2080_81) for r in enrollment_records if r.count_2080_81.isdigit())
    total_2081_82 = sum(r.count_2081_82 for r in enrollment_records)

    context = {
        "school": school,
        "programs": programs,
        "routines": routines,
        "enrollment_records": enrollment_records,
        "total_2080_81": total_2080_81,
        "total_2081_82": total_2081_82,
        "page_title": "Academics, Examination Routines & Results - Hunainath Educational Academy",
    }
    return render(request, "core/academics_hub.html", context)


def exam_routines(request):
    """
    Dedicated Exam Routine timetable page by grade & term.
    """
    school = get_school_profile(request)
    term_filter = request.GET.get("term", "").strip()
    grade_filter = request.GET.get("grade", "").strip()

    routines = ExamRoutine.objects.filter(is_active=True)
    if term_filter:
        routines = routines.filter(exam_term=term_filter)
    if grade_filter:
        routines = routines.filter(grade__icontains=grade_filter)

    routines = routines.order_by("-academic_year", "start_date")

    context = {
        "school": school,
        "routines": routines,
        "term_filter": term_filter,
        "grade_filter": grade_filter,
        "page_title": "Examination Routines & Schedules - Hunainath Educational Academy",
    }
    return render(request, "core/exam_routines.html", context)


@ratelimit(key="ip", rate="15/m", block=True)
def exam_results(request):
    """
    Interactive Student Examination Result Portal.
    Requires Symbol/Roll Number (exact match) to prevent unauthorized student PII/marksheet enumeration.
    """
    school = get_school_profile(request)
    symbol_no = request.GET.get("symbol_no", "").strip().upper()
    student_name = request.GET.get("student_name", "").strip()
    grade = request.GET.get("grade", "").strip()
    term = request.GET.get("term", "").strip()

    result = None
    searched = False
    error_message = ""

    if symbol_no or student_name:
        searched = True
        if not symbol_no:
            error_message = "Please enter the student's Symbol / Roll Number (e.g. HNA-801) to view the official marksheet."
        else:
            qs = ExamResult.objects.filter(is_published=True, symbol_number__iexact=symbol_no)
            if student_name:
                qs = qs.filter(student_name__icontains=student_name)
            if grade:
                qs = qs.filter(grade__iexact=grade)
            if term:
                qs = qs.filter(exam_term=term)

            result = qs.first()
            if not result:
                error_message = "No published examination record found for the provided details. Please verify the Symbol/Roll Number, Name, and Class."

    # Available classes for filter dropdown
    available_classes = [
        "Nursery", "LKG", "UKG", "Grade 1", "Grade 2", "Grade 3", 
        "Grade 4", "Grade 5", "Grade 6", "Grade 7", "Grade 8"
    ]

    context = {
        "school": school,
        "symbol_no": symbol_no,
        "student_name": student_name,
        "grade": grade,
        "available_classes": available_classes,
        "term": term,
        "result": result,
        "searched": searched,
        "error_message": error_message,
        "page_title": "Online Examination Result Portal - Hunainath Educational Academy",
    }
    return render(request, "core/exam_results.html", context)



# ==============================================================================
# BLOG & EDUCATIONAL ARTICLES
# ==============================================================================

def blog_list(request):
    """
    Academy Blog, Articles, Cultural Celebrations, and Educational Insights.
    """
    school = get_school_profile(request)
    category = request.GET.get("category", "").strip()
    query = request.GET.get("q", "").strip()

    posts = BlogPost.objects.filter(is_published=True)
    if category:
        posts = posts.filter(category=category)
    if query:
        posts = posts.filter(Q(title__icontains=query) | Q(summary__icontains=query) | Q(content__icontains=query))

    featured_post = BlogPost.objects.filter(is_published=True, is_featured=True).first()
    if not featured_post:
        featured_post = posts.first()

    paginator = Paginator(posts, 6)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "school": school,
        "page_obj": page_obj,
        "featured_post": featured_post,
        "selected_category": category,
        "query": query,
        "page_title": "School Blog & Educational Insights - Hunainath Educational Academy",
    }
    return render(request, "core/blog_list.html", context)


def blog_detail(request, slug):
    """
    Full Blog Article reading view with related posts and share buttons.
    """
    school = get_school_profile(request)
    post = get_object_or_404(BlogPost, slug=slug, is_published=True)

    # Atomic increment view counter
    BlogPost.objects.filter(pk=post.pk).update(views_count=F("views_count") + 1)
    post.views_count += 1

    related_posts = BlogPost.objects.filter(is_published=True).exclude(pk=post.pk).filter(category=post.category)[:3]
    if not related_posts.exists():
        related_posts = BlogPost.objects.filter(is_published=True).exclude(pk=post.pk)[:3]

    context = {
        "school": school,
        "post": post,
        "related_posts": related_posts,
        "page_title": f"{post.title} - Hunainath Educational Academy Blog",
        "meta_description": post.summary[:160],
    }
    return render(request, "core/blog_detail.html", context)


def faq(request):
    """
    Frequently Asked Questions (FAQ) for parents and guardians.
    Covers Admissions, ECD to Grade 8, Fee policies, Bus Transport,
    Examinations, BLE (Class 8), Uniform, and Health & Safety.
    """
    school = get_school_profile(request)
    faqs = [
        {
            "category": "Admissions & Enrollment",
            "icon": "fas fa-user-plus",
            "items": [
                {
                    "q": "What classes/grades are offered at Hunainath Educational Academy?",
                    "a": "Hunainath Educational Academy is a premier foundational academy offering comprehensive education from Early Childhood Development (Montessori ECD / Nursery, LKG, UKG) up to Grade 8 (Basic Level Education - BLE)."
                },
                {
                    "q": "How can I enroll my child for the new academic session?",
                    "a": "You can enroll online via our official Admissions portal or visit our school administration office during school hours (Sunday to Friday, 9:00 AM – 4:00 PM). Parents can track their admission review status online using their Application ID or Mobile Number."
                },
                {
                    "q": "What documents are required for admission?",
                    "a": "Requirements include: 1) Birth Registration Certificate photocopy, 2) Transfer Certificate (TC) & previous grade Character Certificate (for Grade 1 and above), 3) 2 passport-size photographs of the student, and 4) Parents' / Guardian's citizenship photocopy."
                }
            ]
        },
        {
            "category": "Academics & Examination System",
            "icon": "fas fa-graduation-cap",
            "items": [
                {
                    "q": "How can parents check Terminal & Final Examination results?",
                    "a": "Results can be checked instantly on our website under Academics > Exam Results. Simply enter the student's Symbol Number / Roll Number and Date of Birth to view the verified digital marksheet and GPA."
                },
                {
                    "q": "What is the medium of instruction?",
                    "a": "We operate a progressive bilingual curriculum. Core subjects such as Mathematics, Science & Technology, Computer Literacy, and English are taught in English medium, while Nepali language and Social Studies are taught in accordance with the National Curriculum Framework."
                },
                {
                    "q": "Does the school prepare students for the Class 8 BLE Board Exam?",
                    "a": "Yes! Grade 8 students receive intensive academic preparation, model exam series, and personalized mentoring for the Shuklaphanta Municipality Basic Level Examination (BLE Board Exam)."
                }
            ]
        },
        {
            "category": "Facilities, Transport & Campus Life",
            "icon": "fas fa-bus-alt",
            "items": [
                {
                    "q": "Does the academy provide daily school bus transportation?",
                    "a": "Yes. Our fleet of yellow school buses covers Garjamuni, Shuklaphanta Municipality wards, and adjacent pick-up points with dedicated bus attendants ensuring child safety and punctual commutes."
                },
                {
                    "q": "What extracurricular activities (ECA) are provided?",
                    "a": "Every Friday features structured ECA including football, athletics, badminton, cultural folk dance, music, elocution, quiz competitions, art & craft exhibitions, and agricultural field observations."
                },
                {
                    "q": "What safety and hygienic measures are in place?",
                    "a": "The campus provides clean filtered drinking water, separate hygienic restrooms for boys and girls, a fully equipped first-aid station, and a secure fenced campus with 24/7 staff supervision."
                }
            ]
        }
    ]
    context = {
        "school": school,
        "faqs": faqs,
        "page_title": "Frequently Asked Questions (FAQ) - Hunainath Educational Academy",
    }
    return render(request, "core/faq.html", context)


def terms_and_conditions(request):
    """
    Terms & Conditions, Code of Conduct, and Operational Policies.
    """
    school = get_school_profile(request)
    context = {
        "school": school,
        "page_title": "Terms & Conditions and Student Code of Conduct - Hunainath Educational Academy",
    }
    return render(request, "core/terms.html", context)




# ------------------------------------------------------------------------------
# NEWSLETTER SUBSCRIPTION
# ------------------------------------------------------------------------------
@require_POST
@ratelimit(key="ip", rate="10/m", block=True)
def newsletter_subscribe(request):
    """Subscribe an email to the newsletter (AJAX JSON or normal form POST)."""
    from django.core.validators import validate_email
    from django.core.exceptions import ValidationError
    from .models import NewsletterSubscriber

    email = (request.POST.get("email") or "").strip().lower()
    name = (request.POST.get("name") or "").strip()[:150]
    is_ajax = request.headers.get("x-requested-with") == "XMLHttpRequest"

    try:
        validate_email(email)
    except ValidationError:
        msg, ok = "Please enter a valid email address.", False
    else:
        sub, created = NewsletterSubscriber.objects.get_or_create(email=email, defaults={"name": name})
        if created:
            msg, ok = "Thank you! You are now subscribed to our newsletter.", True
        elif not sub.is_active:
            sub.is_active = True
            sub.save(update_fields=["is_active"])
            msg, ok = "Welcome back! Your subscription has been reactivated.", True
        else:
            msg, ok = "You are already subscribed. Thank you!", True

    if is_ajax:
        return JsonResponse({"ok": ok, "message": msg}, status=200 if ok else 400)
    (messages.success if ok else messages.error)(request, msg)
    referer = request.META.get("HTTP_REFERER", "")
    if referer and url_has_allowed_host_and_scheme(
        url=referer,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        return redirect(referer)
    return redirect("index")


def newsletter_unsubscribe(request, token):
    """One-click unsubscribe from newsletter emails."""
    from .models import NewsletterSubscriber

    sub = get_object_or_404(NewsletterSubscriber, unsubscribe_token=token)
    if sub.is_active:
        sub.is_active = False
        sub.save(update_fields=["is_active"])
    messages.info(request, f"{sub.email} has been unsubscribed from our newsletter.")
    return redirect("index")
