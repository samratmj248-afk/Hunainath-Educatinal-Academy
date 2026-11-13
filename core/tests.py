"""
Comprehensive QA, Backend, SEO, Performance, and Security Test Suite
for Shree Hunainath Educational Academy.
"""

import json
from datetime import date
from django.test import TestCase, Client
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile

from .models import (
    SchoolProfile,
    Notice,
    AcademicProgram,
    AdmissionApplication,
    BlogPost,
    ExamResult,
    NewsletterSubscriber,
    ContactInquiry,
    PushSubscription,
)


class AcademyQATestSuite(TestCase):
    def setUp(self):
        self.client = Client(HTTP_HOST="localhost")
        self.school = SchoolProfile.objects.create(
            name="Shree Hunainath Educational Academy",
            principal_name="Bashu Dev Bhatt",
        )
        self.program = AcademicProgram.objects.create(
            title="Primary Level",
            level="PRIMARY",
            grade_span="Classes 1 - 5",
            short_summary="Comprehensive foundational primary curriculum.",
            detailed_curriculum="English, Nepali, Science, Mathematics.",
        )
        self.notice = Notice.objects.create(
            title="Annual Examination Notice 2083",
            category="EXAM",
            content="Examinations start from Chaitra 10.",
            is_active=True,
            is_ticker=True,
        )
        self.blog = BlogPost.objects.create(
            title="STEM Learning at Hunainath",
            category="STEM",
            summary="Hands-on science and computer education.",
            content="Detailed article on STEM education.",
            is_published=True,
        )
        self.exam_result = ExamResult.objects.create(
            student_name="Aarav Joshi",
            symbol_number="HNA-801",
            date_of_birth=date(2012, 5, 14),
            grade="Grade 8",
            gpa=3.90,
            grade_letter="A+",
            is_published=True,
        )

    def test_public_pages_status_and_headers(self):
        """Verify all public routes return 200 OK and include enterprise security headers."""
        public_urls = [
            reverse("index"),
            reverse("about"),
            reverse("programs"),
            reverse("program_detail", args=[self.program.slug]),
            reverse("academics_hub"),
            reverse("exam_routines"),
            reverse("exam_results"),
            reverse("blog_list"),
            reverse("blog_detail", args=[self.blog.slug]),
            reverse("admissions"),
            reverse("admission_status"),
            reverse("notices"),
            reverse("notice_detail", args=[self.notice.slug]),
            reverse("gallery"),
            reverse("faculty"),
            reverse("contact"),
            reverse("faq"),
            reverse("terms_and_conditions"),
            reverse("service_worker"),
            reverse("manifest_json"),
            reverse("offline"),
            reverse("push_vapid_key"),
            reverse("robots_txt"),
            reverse("sitemap_xml"),
        ]
        for url in public_urls:
            resp = self.client.get(url)
            self.assertEqual(resp.status_code, 200, f"Failed on {url}")
            self.assertIn("Content-Security-Policy", resp.headers)
            self.assertEqual(resp.headers.get("X-Content-Type-Options"), "nosniff")
            if resp.headers.get("Content-Type", "").startswith("text/html"):
                body = resp.content.decode("utf-8")
                self.assertNotIn("{{", body, f"Unrendered Django variable tag on {url}")
                self.assertNotIn("{%", body, f"Unrendered Django block tag on {url}")

    def test_seo_canonical_and_sitemap(self):
        """Verify canonical tag in HTML and complete coverage in sitemap.xml."""
        resp = self.client.get(reverse("index"))
        self.assertContains(resp, '<link rel="canonical" href="http://localhost/">')

        sitemap_resp = self.client.get(reverse("sitemap_xml"))
        self.assertEqual(sitemap_resp.status_code, 200)
        self.assertIn(f"/blog/{self.blog.slug}/", sitemap_resp.content.decode())
        self.assertIn(f"/notices/{self.notice.slug}/", sitemap_resp.content.decode())
        self.assertIn(f"/programs/{self.program.slug}/", sitemap_resp.content.decode())

    def test_atomic_view_counters(self):
        """Verify notice and blog detail views increment views_count atomically."""
        initial_notice_views = self.notice.views_count
        self.client.get(reverse("notice_detail", args=[self.notice.slug]))
        self.notice.refresh_from_db()
        self.assertEqual(self.notice.views_count, initial_notice_views + 1)

        initial_blog_views = self.blog.views_count
        self.client.get(reverse("blog_detail", args=[self.blog.slug]))
        self.blog.refresh_from_db()
        self.assertEqual(self.blog.views_count, initial_blog_views + 1)

    def test_exam_results_blocks_name_only_enumeration(self):
        """Ensure searching by partial student name without symbol_no does not leak student marksheets."""
        resp_no_symbol = self.client.get(reverse("exam_results"), {"student_name": "Aarav"})
        self.assertIsNone(resp_no_symbol.context["result"])
        self.assertIn("Symbol / Roll Number", resp_no_symbol.context["error_message"])

        resp_with_symbol = self.client.get(reverse("exam_results"), {"symbol_no": "HNA-801"})
        self.assertEqual(resp_with_symbol.context["result"], self.exam_result)

    def test_admissions_honeypot_and_file_validation(self):
        """Verify admission submission, honeypot protection, and malicious file upload rejection."""
        bad_file = SimpleUploadedFile("exploit.html", b"<script>alert(1)</script>", content_type="text/html")
        resp_bad = self.client.post(
            reverse("admissions"),
            {
                "student_name": "Test Student",
                "date_of_birth": "2015-04-10",
                "gender": "MALE",
                "grade_applying_for": "Grade 3",
                "parent_name": "Parent Name",
                "parent_phone": "9800000000",
                "address": "Garjamuni",
                "birth_certificate": bad_file,
            },
        )
        self.assertEqual(AdmissionApplication.objects.count(), 0)

        valid_pdf = SimpleUploadedFile("birth.pdf", b"%PDF-1.4 valid content", content_type="application/pdf")
        resp_ok = self.client.post(
            reverse("admissions"),
            {
                "student_name": "Valid Student",
                "date_of_birth": "2015-04-10",
                "gender": "FEMALE",
                "grade_applying_for": "Grade 3",
                "parent_name": "Parent Name",
                "parent_phone": "9800000000",
                "address": "Garjamuni",
                "birth_certificate": valid_pdf,
            },
        )
        self.assertEqual(resp_ok.status_code, 200)
        self.assertEqual(AdmissionApplication.objects.count(), 1)

    def test_admin_qr_routes_require_staff_authentication(self):
        """Ensure anonymous users cannot access admin QR standee or download endpoints."""
        resp_standee = self.client.get(reverse("admin_qr_standee"))
        self.assertEqual(resp_standee.status_code, 302)

        resp_qr = self.client.get(reverse("admin_qr_download"))
        self.assertEqual(resp_qr.status_code, 302)

    def test_newsletter_open_redirect_protection(self):
        """Ensure newsletter_subscribe blocks external malicious HTTP_REFERER redirects."""
        resp = self.client.post(
            reverse("newsletter_subscribe"),
            {"email": "parent@example.com", "name": "Parent"},
            HTTP_REFERER="https://evil-phishing.example.com/login",
        )
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.url, reverse("index"))
        self.assertTrue(NewsletterSubscriber.objects.filter(email="parent@example.com").exists())

    def test_push_subscribe_validates_https_endpoint(self):
        """Verify push_subscribe rejects non-HTTPS or malformed endpoints."""
        resp_invalid = self.client.post(
            reverse("push_subscribe"),
            data=json.dumps({"endpoint": "http://insecure.local/push", "keys": {"p256dh": "k1", "auth": "a1"}}),
            content_type="application/json",
        )
        self.assertEqual(resp_invalid.status_code, 400)

        resp_valid = self.client.post(
            reverse("push_subscribe"),
            data=json.dumps(
                {"endpoint": "https://fcm.googleapis.com/fcm/send/123", "keys": {"p256dh": "k1", "auth": "a1"}}
            ),
            content_type="application/json",
        )
        self.assertEqual(resp_valid.status_code, 200)
        self.assertEqual(PushSubscription.objects.count(), 1)
