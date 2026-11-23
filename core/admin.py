"""
Django Unfold Admin Customization for Shree Hunainath Educational Academy.
Provides modern Tailwind styling, badges, filters, search, and bulk management.
"""

from django.contrib import admin
from django.utils.html import format_html
from django.contrib import messages
from django.contrib.auth.models import Group, User
from django.contrib.auth.admin import GroupAdmin as BaseGroupAdmin, UserAdmin as BaseUserAdmin
from unfold.admin import ModelAdmin
from unfold.decorators import display
from unfold.forms import UserChangeForm, UserCreationForm, AdminPasswordChangeForm

# Unregister default Django Auth admins and re-register with Unfold ModelAdmin
admin.site.unregister(Group)
admin.site.unregister(User)


@admin.register(Group)
class GroupAdmin(ModelAdmin, BaseGroupAdmin):
    pass


@admin.register(User)
class UserAdmin(ModelAdmin, BaseUserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm
    change_password_form = AdminPasswordChangeForm

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


@admin.register(SchoolProfile)
class SchoolProfileAdmin(ModelAdmin):
    list_display = ("name", "name_nepali", "phone", "email", "stats_students", "stats_pass_rate")
    fieldsets = (
        (
            "Institution Identity",
            {
                "fields": (
                    ("name", "name_nepali"),
                    "tagline",
                    ("established_year", "affiliation"),
                    "logo",
                )
            },
        ),
        (
            "Contact & Location",
            {
                "fields": (
                    ("phone", "mobile"),
                    "email",
                    "address",
                    "google_maps_url",
                )
            },
        ),
        (
            "Social Media Channels",
            {
                "fields": (
                    ("facebook_url", "instagram_url"),
                    ("youtube_url", "whatsapp_number"),
                )
            },
        ),
        (
            "Principal & Leadership",
            {
                "fields": (
                    ("principal_name", "principal_designation"),
                    "principal_photo",
                    "principal_message",
                )
            },
        ),
        (
            "About, Mission & Vision",
            {
                "fields": (
                    "about_text",
                    "mission",
                    "vision",
                )
            },
        ),
        (
            "Key Metric Counters",
            {
                "fields": (
                    ("stats_students", "stats_faculty"),
                    ("stats_pass_rate", "stats_years_excellence"),
                )
            },
        ),
    )


@admin.register(Notice)
class NoticeAdmin(ModelAdmin):
    list_display = (
        "title",
        "category_badge",
        "priority_badge",
        "is_ticker_status",
        "is_active_status",
        "published_at",
        "views_count",
    )
    list_filter = ("category", "priority", "is_ticker", "is_active", "published_at")
    search_fields = ("title", "content")
    prepopulated_fields = {"slug": ("title",)}
    actions = ["make_active", "make_inactive", "enable_ticker", "disable_ticker", "broadcast_push_notice"]

    def save_model(self, request, obj, form, change):
        is_new = obj.pk is None
        super().save_model(request, obj, form, change)
        # When creating a new active notice or urgent ticker, automatically broadcast push notification with chime sound
        if (is_new or not change) and obj.is_active:
            try:
                from .views import send_web_push_notification
                notice_url = f"/notices/{obj.slug}/" if obj.slug else "/notices/"
                count = send_web_push_notification(
                    title=f"📢 Notice: {obj.title}",
                    body=obj.content[:140] if obj.content else "A new official notice has been published by Shree Hunainath Academy.",
                    url=notice_url
                )
                if count > 0:
                    messages.success(request, f"🔔 Web push notification with audio chime broadcast to {count} device(s)!")
            except Exception as e:
                print(f"[NoticeAdmin] Broadcast push error: {e}")

    @admin.action(description="🔔 Broadcast push notification & ring chime for selected notices")
    def broadcast_push_notice(self, request, queryset):
        from .views import send_web_push_notification
        total_sent = 0
        for obj in queryset:
            notice_url = f"/notices/{obj.slug}/" if obj.slug else "/notices/"
            sent = send_web_push_notification(
                title=f"📢 Notice: {obj.title}",
                body=obj.content[:140] if obj.content else "Official announcement from Shree Hunainath Academy.",
                url=notice_url
            )
            total_sent += sent
        messages.success(request, f"🔔 Successfully broadcast notice push notification to {total_sent} subscriber device(s)!")

    @display(description="Category", label=True)
    def category_badge(self, obj):
        colors = {
            "ACADEMIC": "info",
            "EXAM": "warning",
            "ADMISSION": "success",
            "EVENT": "secondary",
            "HOLIDAY": "primary",
            "URGENT": "danger",
        }
        return obj.get_category_display()

    @display(description="Priority", label=True)
    def priority_badge(self, obj):
        return obj.get_priority_display()

    @display(description="Urgent Ticker", boolean=True)
    def is_ticker_status(self, obj):
        return obj.is_ticker

    @display(description="Active", boolean=True)
    def is_active_status(self, obj):
        return obj.is_active

    @admin.action(description="Mark selected notices as Active")
    def make_active(self, request, queryset):
        queryset.update(is_active=True)

    @admin.action(description="Mark selected notices as Inactive")
    def make_inactive(self, request, queryset):
        queryset.update(is_active=False)

    @admin.action(description="Display in Top Urgent News Ticker")
    def enable_ticker(self, request, queryset):
        queryset.update(is_ticker=True)

    @admin.action(description="Remove from Top Urgent News Ticker")
    def disable_ticker(self, request, queryset):
        queryset.update(is_ticker=False)


@admin.register(AcademicProgram)
class AcademicProgramAdmin(ModelAdmin):
    list_display = ("title", "level", "grade_span", "order", "is_featured")
    list_filter = ("level", "is_featured")
    search_fields = ("title", "short_summary", "detailed_curriculum")
    prepopulated_fields = {"slug": ("title",)}
    list_editable = ("order", "is_featured")


@admin.register(StudentEnrollmentRecord)
class StudentEnrollmentRecordAdmin(ModelAdmin):
    list_display = ("order", "grade_name", "count_2080_81", "count_2081_82", "highlight_badge")
    list_editable = ("grade_name", "count_2080_81", "count_2081_82", "highlight_badge")
    ordering = ("order",)


@admin.register(AdmissionApplication)
class AdmissionApplicationAdmin(ModelAdmin):
    list_display = (
        "reference_id",
        "student_name",
        "grade_applying_for",
        "parent_name",
        "parent_phone",
        "status_badge",
        "created_at",
    )
    list_filter = ("status", "grade_applying_for", "gender", "created_at")
    search_fields = ("reference_id", "student_name", "parent_name", "parent_phone", "address")
    readonly_fields = ("reference_id", "created_at", "updated_at")
    actions = ["mark_under_review", "mark_accepted", "mark_declined"]

    @display(description="Status", label=True)
    def status_badge(self, obj):
        return obj.get_status_display()

    @admin.action(description="Mark status as Under Review")
    def mark_under_review(self, request, queryset):
        queryset.update(status="UNDER_REVIEW")

    @admin.action(description="Accept selected applications")
    def mark_accepted(self, request, queryset):
        queryset.update(status="ACCEPTED")

    @admin.action(description="Decline selected applications")
    def mark_declined(self, request, queryset):
        queryset.update(status="REJECTED")


@admin.register(GalleryItem)
class GalleryItemAdmin(ModelAdmin):
    list_display = ("title", "category", "is_featured", "order", "created_at")
    list_filter = ("category", "is_featured")
    search_fields = ("title", "caption")
    list_editable = ("is_featured", "order")


@admin.register(FacultyMember)
class FacultyMemberAdmin(ModelAdmin):
    list_display = ("name", "designation", "department", "qualification", "is_leadership", "order")
    list_filter = ("department", "is_leadership")
    search_fields = ("name", "designation", "qualification", "bio")
    list_editable = ("order", "is_leadership")


@admin.register(Testimonial)
class TestimonialAdmin(ModelAdmin):
    list_display = ("name", "role", "rating", "is_featured", "order")
    list_filter = ("rating", "is_featured")
    search_fields = ("name", "role", "quote")
    list_editable = ("is_featured", "order")


@admin.register(ContactInquiry)
class ContactInquiryAdmin(ModelAdmin):
    list_display = ("name", "subject", "phone", "email", "is_read", "replied", "created_at")
    list_filter = ("is_read", "replied", "created_at")
    search_fields = ("name", "email", "phone", "subject", "message")
    readonly_fields = ("name", "email", "phone", "subject", "message", "created_at")
    actions = ["mark_as_read", "mark_as_replied"]

    @admin.action(description="Mark selected messages as read")
    def mark_as_read(self, request, queryset):
        queryset.update(is_read=True)

    @admin.action(description="Mark selected messages as replied")
    def mark_as_replied(self, request, queryset):
        queryset.update(replied=True)


@admin.register(PushSubscription)
class PushSubscriptionAdmin(ModelAdmin):
    list_display = ("id", "subscriber_endpoint", "is_active", "created_at")
    list_filter = ("is_active", "created_at")
    search_fields = ("endpoint", "user_agent")

    @display(description="Endpoint URL")
    def subscriber_endpoint(self, obj):
        return obj.endpoint[:45] + ("..." if len(obj.endpoint) > 45 else "")


@admin.register(BroadcastNotification)
class BroadcastNotificationAdmin(ModelAdmin):
    list_display = ("title", "url", "sent_count", "created_at")
    search_fields = ("title", "body")
    actions = ["dispatch_notification"]

    def save_model(self, request, obj, form, change):
        is_new = obj.pk is None
        super().save_model(request, obj, form, change)
        if is_new:
            from .views import send_web_push_notification
            count = send_web_push_notification(obj.title, obj.body, obj.url)
            obj.sent_count = count
            obj.save(update_fields=["sent_count"])
            messages.success(request, f"🔔 Notification sent instantly to {count} device(s) with audio chime.")

    @admin.action(description="Broadcast this notification to all active web push subscribers")
    def dispatch_notification(self, request, queryset):
        from .views import send_web_push_notification

        total_sent = 0
        for notification in queryset:
            count = send_web_push_notification(notification.title, notification.body, notification.url)
            notification.sent_count += count
            notification.save()
            total_sent += count
        messages.success(request, f"Notification dispatched successfully to {total_sent} push subscribers.")


@admin.register(BlogPost)
class BlogPostAdmin(ModelAdmin):
    list_display = ("title", "category", "author_name", "is_published", "is_featured", "published_at")
    list_filter = ("category", "is_published", "is_featured", "published_at")
    search_fields = ("title", "summary", "content", "author_name")
    prepopulated_fields = {"slug": ("title",)}


@admin.register(ExamRoutine)
class ExamRoutineAdmin(ModelAdmin):
    list_display = ("title", "grade", "exam_term", "academic_year", "start_date", "end_date", "is_active")
    list_filter = ("exam_term", "academic_year", "is_active")
    search_fields = ("title", "grade", "instructions")
    fieldsets = (
        ("Routine Information", {
            "fields": (
                "title",
                ("exam_term", "academic_year"),
                "grade",
                ("start_date", "end_date"),
                "is_active",
            )
        }),
        ("Routine Uploads (PDF & Image)", {
            "fields": (
                "routine_pdf",
                "routine_image",
            ),
            "description": "Upload an official routine PDF file and/or a readable image timetable for students and parents."
        }),
        ("Exam Instructions & Hall Rules", {
            "fields": (
                "instructions",
            )
        }),
    )

    def save_model(self, request, obj, form, change):
        is_new = obj.pk is None
        super().save_model(request, obj, form, change)
        if (is_new or not change) and obj.is_active:
            try:
                from .views import send_web_push_notification
                count = send_web_push_notification(
                    title=f"📅 Exam Routine: {obj.title}",
                    body=f"New exam timetable published for {obj.grade} ({obj.get_exam_term_display()}). Tap to view/download.",
                    url="/academics/routines/"
                )
                if count > 0:
                    messages.success(request, f"🔔 Web push notification with audio chime broadcast to {count} device(s)!")
            except Exception as e:
                print(f"[ExamRoutineAdmin] Broadcast push error: {e}")


@admin.register(ExamResult)
class ExamResultAdmin(ModelAdmin):
    list_display = ("student_name", "symbol_number", "grade", "academic_year", "exam_term", "gpa", "grade_letter", "result_status", "is_published")
    list_filter = ("grade", "academic_year", "exam_term", "result_status", "is_published")
    search_fields = ("student_name", "symbol_number", "grade", "remarks")



# ------------------------------------------------------------------------------
# NEWSLETTER
# ------------------------------------------------------------------------------
from .models import NewsletterSubscriber, Newsletter  # noqa: E402


@admin.register(NewsletterSubscriber)
class NewsletterSubscriberAdmin(ModelAdmin):
    list_display = ("email", "name", "is_active", "subscribed_at")
    list_filter = ("is_active", "subscribed_at")
    search_fields = ("email", "name")
    list_editable = ("is_active",)
    readonly_fields = ("unsubscribe_token", "subscribed_at")
    actions = ["activate", "deactivate"]

    @admin.action(description="Activate selected subscribers")
    def activate(self, request, queryset):
        self.message_user(request, f"{queryset.update(is_active=True)} subscriber(s) activated.")

    @admin.action(description="Deactivate selected subscribers")
    def deactivate(self, request, queryset):
        self.message_user(request, f"{queryset.update(is_active=False)} subscriber(s) deactivated.")


@admin.register(Newsletter)
class NewsletterAdmin(ModelAdmin):
    list_display = ("subject", "status", "recipients_count", "sent_at", "created_at")
    list_filter = ("status",)
    search_fields = ("subject", "content")
    readonly_fields = ("status", "recipients_count", "sent_at", "created_at")
    fields = ("subject", "preheader", "cover_image", "content", "status", "recipients_count", "sent_at", "created_at")
    actions = ["send_to_subscribers", "send_test_to_me"]

    @admin.action(description="Send selected newsletter(s) to all active subscribers")
    def send_to_subscribers(self, request, queryset):
        from .newsletter import send_newsletter

        total_active = NewsletterSubscriber.objects.filter(is_active=True).count()
        if not total_active:
            self.message_user(request, "There are no active subscribers yet.", messages.WARNING)
            return
        for nl in queryset:
            try:
                sent = send_newsletter(nl, request=request)
                self.message_user(request, f"'{nl.subject}' sent to {sent} subscriber(s).", messages.SUCCESS)
            except Exception as exc:  # SMTP / network errors
                self.message_user(request, f"Failed to send '{nl.subject}': {exc}", messages.ERROR)

    @admin.action(description="Send a test email to my admin address")
    def send_test_to_me(self, request, queryset):
        from .newsletter import send_newsletter

        if not request.user.email:
            self.message_user(request, "Add an email address to your admin user first.", messages.WARNING)
            return
        test_sub = NewsletterSubscriber(email=request.user.email, name=request.user.get_full_name())
        for nl in queryset:
            try:
                send_newsletter(nl, request=request, recipients=[test_sub])
                self.message_user(request, f"Test of '{nl.subject}' sent to {request.user.email}.", messages.SUCCESS)
            except Exception as exc:
                self.message_user(request, f"Test send failed: {exc}", messages.ERROR)
