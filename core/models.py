"""
Data Models for Shree Hunainath Educational Academy.
Covers School Profile, Notices, Academic Programs, Admissions,
Gallery, Faculty, Testimonials, Push Subscriptions, and Inquiries.
"""

import uuid
from django.db import models
from django.utils.text import slugify


class SchoolProfile(models.Model):
    """
    Singleton model containing institutional identity, contact, leadership, and stats.
    """
    name = models.CharField(max_length=255, default="Shree Hunainath Educational Academy")
    name_nepali = models.CharField(max_length=255, default="श्री हुनैनाथ एजुकेसनल एकेडेमी")
    tagline = models.CharField(
        max_length=255,
        default="Empowering Minds, Inspiring Futures • ज्ञान, संस्कार र उत्कृष्टता",
    )
    established_year = models.PositiveIntegerField(default=2008)
    affiliation = models.CharField(max_length=255, default="Government of Nepal, Ministry of Education & NEB")
    
    # Contact info
    phone = models.CharField(max_length=50, default="+977-99-402120")
    mobile = models.CharField(max_length=50, default="+977-9848712345")
    email = models.EmailField(default="info@hunainath.edu.np")
    address = models.CharField(
        max_length=300,
        default="Shuklaphanta Municipality-5, Garjamani, Kanchanpur, Sudurpashchim Province, Nepal",
    )
    google_maps_url = models.URLField(
        blank=True,
        default="https://maps.google.com/?q=Shuklaphanta+Garjamani+Kanchanpur+Nepal",
    )

    # Social links
    facebook_url = models.URLField(default="https://www.facebook.com/hunainath.school")
    instagram_url = models.URLField(default="https://www.instagram.com/hunainathschool/", blank=True)
    youtube_url = models.URLField(blank=True, default="https://youtube.com")
    whatsapp_number = models.CharField(max_length=50, default="+9779848701283")

    # Leadership & Principal
    principal_name = models.CharField(max_length=150, default="Padam Raj Joshi")
    principal_designation = models.CharField(max_length=100, default="Principal & Academic Director")
    principal_message = models.TextField(
        default=(
            "Welcome to Shree Hunainath Educational Academy! We are passionately dedicated to nurturing "
            "academic brilliance, moral integrity, creative intellect, and social responsibility in every "
            "student. Here in Garjamani, Kanchanpur, we provide modern laboratories, smart classrooms, "
            "inspirational educators, and an inclusive learning community where your child's highest potential "
            "is unlocked."
        )
    )
    principal_photo = models.ImageField(upload_to="leadership/", blank=True, null=True)

    # About & Mission
    about_text = models.TextField(
        default=(
            "Shree Hunainath Educational Academy is a premier educational institution situated in "
            "Shuklaphanta-5, Garjamani, Kanchanpur. Founded with a vision to provide world-class foundational "
            "and secondary education in Sudurpashchim Province, the academy combines rigorous academic "
            "curricula with hands-on STEM learning, creative arts, and athletic excellence."
        )
    )
    mission = models.TextField(
        default="To deliver holistic, transformative education that equips students with critical thinking, ethical fortitude, and 21st-century skills."
    )
    vision = models.TextField(
        default="To stand as an exemplary center of academic distinction, scientific inquiry, and cultural pride in western Nepal."
    )

    # Key Achievement Metrics
    stats_students = models.PositiveIntegerField(default=1250, help_text="Total active students")
    stats_faculty = models.PositiveIntegerField(default=52, help_text="Total certified teachers")
    stats_pass_rate = models.CharField(max_length=20, default="100%", help_text="SEE / Board Success Rate")
    stats_years_excellence = models.PositiveIntegerField(default=18, help_text="Years serving the community")

    logo = models.ImageField(upload_to="branding/", blank=True, null=True)

    class Meta:
        verbose_name = "School Profile & Settings"
        verbose_name_plural = "School Profile & Settings"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # Guarantee singleton pattern
        if not self.pk and SchoolProfile.objects.exists():
            return SchoolProfile.objects.first()
        return super().save(*args, **kwargs)


class Notice(models.Model):
    """
    Notices, circulars, exam schedules, and urgent tickers.
    """
    CATEGORY_CHOICES = [
        ("ACADEMIC", "Academic Routine & Calendar"),
        ("EXAM", "Examinations & Results"),
        ("ADMISSION", "Admissions & Intake"),
        ("EVENT", "Campus Events & Sports"),
        ("HOLIDAY", "Holidays & Vacations"),
        ("URGENT", "Urgent Announcement"),
    ]

    PRIORITY_CHOICES = [
        ("NORMAL", "Standard Notice"),
        ("HIGH", "High Importance"),
        ("EMERGENCY", "Urgent / Emergency"),
    ]

    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=270, unique=True, blank=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default="ACADEMIC")
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default="NORMAL")
    content = models.TextField()
    attachment = models.FileField(upload_to="notices/documents/", blank=True, null=True)
    is_active = models.BooleanField(default=True, help_text="Visible on the website")
    is_ticker = models.BooleanField(default=False, help_text="Show in top urgent marquee ticker")
    published_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    views_count = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["-priority", "-published_at"]
        verbose_name = "Notice & Circular"
        verbose_name_plural = "Notices & Circulars"

    def __str__(self):
        return f"[{self.category}] {self.title}"

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title) or "notice"
            candidate = base_slug
            idx = 1
            while Notice.objects.filter(slug=candidate).exclude(pk=self.pk).exists():
                candidate = f"{base_slug}-{idx}"
                idx += 1
            self.slug = candidate
        super().save(*args, **kwargs)


class AcademicProgram(models.Model):
    """
    School levels: ECE, Primary, Lower Secondary, Secondary SEE, and +2 Career streams.
    """
    LEVEL_CHOICES = [
        ("ECE", "Early Childhood Education (Playgroup - UKG)"),
        ("PRIMARY", "Primary School (Class 1 - 5)"),
        ("LOWER_SEC", "Lower Secondary (Class 6 - 8 / BLE Prep)"),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default="PRIMARY")
    grade_span = models.CharField(max_length=100, default="Classes 1 - 5")
    short_summary = models.TextField(help_text="Catchy 2-line description for homepage cards")
    detailed_curriculum = models.TextField(help_text="Comprehensive details and subjects")
    icon = models.CharField(
        max_length=50,
        default="fa-graduation-cap",
        help_text="Font Awesome class, e.g. fa-book-open, fa-flask, fa-laptop-code",
    )
    image = models.ImageField(upload_to="programs/", blank=True, null=True)
    features_list = models.TextField(
        default="Smart Classrooms\nExperienced Faculty\nInteractive Practical Labs\nContinuous Assessment",
        help_text="Enter features separated by line breaks",
    )
    order = models.PositiveIntegerField(default=0)
    is_featured = models.BooleanField(default=True)

    class Meta:
        ordering = ["order", "id"]
        verbose_name = "Academic Program"
        verbose_name_plural = "Academic Programs"

    def __str__(self):
        return f"{self.title} ({self.grade_span})"

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title) or "program"
            candidate = base_slug
            idx = 1
            while AcademicProgram.objects.filter(slug=candidate).exclude(pk=self.pk).exists():
                candidate = f"{base_slug}-{idx}"
                idx += 1
            self.slug = candidate
        super().save(*args, **kwargs)

    def get_features(self):
        return [f.strip() for f in self.features_list.splitlines() if f.strip()]


class StudentEnrollmentRecord(models.Model):
    """
    Academics and Students statistics tracking enrollment across BS academic years (2080/81 vs 2081/82).
    """
    grade_name = models.CharField(max_length=120, help_text="e.g. Early Childhood Development, 1, 2, ..., 8")
    count_2080_81 = models.CharField(max_length=20, default="-", help_text="Count in 2080/81 BS, or '-' if none")
    count_2081_82 = models.PositiveIntegerField(default=0, help_text="Count in 2081/82 BS")
    order = models.PositiveIntegerField(default=0)
    highlight_badge = models.CharField(max_length=50, blank=True, help_text="e.g. +146% Surge or Foundation")

    class Meta:
        ordering = ["order", "id"]
        verbose_name = "Student Enrollment Record"
        verbose_name_plural = "Student Enrollment Records"

    def __str__(self):
        return f"{self.grade_name}: {self.count_2081_82} students (2081/82 BS)"


class AdmissionApplication(models.Model):
    """
    Online Student Admission Applications submitted by parents.
    """
    GENDER_CHOICES = [
        ("MALE", "Male"),
        ("FEMALE", "Female"),
        ("OTHER", "Other"),
    ]

    STATUS_CHOICES = [
        ("PENDING", "Pending Review"),
        ("UNDER_REVIEW", "Under Review"),
        ("INTERVIEW_SCHEDULED", "Entrance / Interview Scheduled"),
        ("ACCEPTED", "Accepted & Enrolled"),
        ("REJECTED", "Application Declined"),
    ]

    reference_id = models.CharField(max_length=30, unique=True, editable=False)
    student_name = models.CharField(max_length=150)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, default="MALE")
    grade_applying_for = models.CharField(max_length=100)
    previous_school = models.CharField(max_length=200, blank=True)
    previous_gpa = models.CharField(max_length=50, blank=True)

    # Parent / Guardian details
    parent_name = models.CharField(max_length=150)
    parent_phone = models.CharField(max_length=30)
    parent_email = models.EmailField(blank=True)
    parent_occupation = models.CharField(max_length=150, blank=True)
    address = models.TextField()

    # Documents & Remarks
    student_photo = models.ImageField(upload_to="admissions/photos/", blank=True, null=True)
    transfer_certificate = models.FileField(upload_to="admissions/docs/", blank=True, null=True)
    birth_certificate = models.FileField(upload_to="admissions/docs/", blank=True, null=True)
    additional_notes = models.TextField(blank=True)

    # Workflow Status
    status = models.CharField(max_length=25, choices=STATUS_CHOICES, default="PENDING")
    admin_feedback = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Admission Application"
        verbose_name_plural = "Admission Applications"

    def __str__(self):
        return f"{self.reference_id} - {self.student_name} ({self.grade_applying_for})"

    def save(self, *args, **kwargs):
        if not self.reference_id:
            year_suffix = "2026"
            rand_token = uuid.uuid4().hex[:6].upper()
            self.reference_id = f"HNA-{year_suffix}-{rand_token}"
        super().save(*args, **kwargs)


class GalleryItem(models.Model):
    """
    Campus life, sports, science labs, cultural programs, and achievements.
    """
    CATEGORY_CHOICES = [
        ("CAMPUS", "Campus & Learning Environment"),
        ("SPORTS", "Sports & Athletics"),
        ("SCIENCE", "Science & Robotics Labs"),
        ("CULTURAL", "Arts, Music & Culture"),
        ("ACADEMICS", "Classrooms & Learning"),
        ("AWARDS", "Achievements & Honors"),
    ]

    title = models.CharField(max_length=200)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default="CAMPUS")
    image = models.ImageField(upload_to="gallery/")
    caption = models.CharField(max_length=300, blank=True)
    is_featured = models.BooleanField(default=True, help_text="Show in homepage infinite slider")
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["order", "-created_at"]
        verbose_name = "Gallery Photo"
        verbose_name_plural = "Gallery Photos"

    def __str__(self):
        return f"{self.title} ({self.get_category_display()})"


class FacultyMember(models.Model):
    """
    School educators, coordinators, and administrative leaders.
    """
    DEPARTMENT_CHOICES = [
        ("ADMIN", "School Administration & Leadership"),
        ("SCIENCE", "Science & Technology"),
        ("MATHS", "Mathematics & Computing"),
        ("LANGUAGES", "Languages (Nepali, English, Sanskrit)"),
        ("SOCIAL", "Social Studies & Humanities"),
        ("PRIMARY", "Primary & ECE Care"),
        ("SPORTS", "Physical Education & Sports"),
    ]

    name = models.CharField(max_length=150)
    designation = models.CharField(max_length=150)
    department = models.CharField(max_length=20, choices=DEPARTMENT_CHOICES, default="SCIENCE")
    qualification = models.CharField(max_length=200)
    photo = models.ImageField(upload_to="faculty/", blank=True, null=True)
    bio = models.TextField(blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=30, blank=True)
    is_leadership = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["-is_leadership", "order", "name"]
        verbose_name = "Faculty & Staff Member"
        verbose_name_plural = "Faculty & Staff Members"

    def __str__(self):
        return f"{self.name} - {self.designation}"


class Testimonial(models.Model):
    """
    Student, parent, and alumni testimonials.
    """
    name = models.CharField(max_length=150)
    role = models.CharField(max_length=150, help_text="e.g. Parent of Grade 7 Student / SEE Alumnus")
    quote = models.TextField()
    rating = models.PositiveSmallIntegerField(default=5)
    photo = models.ImageField(upload_to="testimonials/", blank=True, null=True)
    is_featured = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "-id"]
        verbose_name = "Testimonial"
        verbose_name_plural = "Testimonials"

    def __str__(self):
        return f"{self.name} ({self.role})"


class ContactInquiry(models.Model):
    """
    Messages submitted through the public Contact Us form.
    """
    name = models.CharField(max_length=150)
    email = models.EmailField()
    phone = models.CharField(max_length=30)
    subject = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    replied = models.BooleanField(default=False)
    admin_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Contact Inquiry"
        verbose_name_plural = "Contact Inquiries"

    def __str__(self):
        return f"Message from {self.name}: {self.subject}"


class PushSubscription(models.Model):
    """
    Web Push PWA subscribers for instant announcements.
    """
    endpoint = models.URLField(max_length=500, unique=True)
    p256dh = models.CharField(max_length=255)
    auth = models.CharField(max_length=255)
    user_agent = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Push Subscription"
        verbose_name_plural = "Push Subscriptions"

    def __str__(self):
        return f"Subscriber {self.id} ({self.endpoint[:35]}...)"


class BroadcastNotification(models.Model):
    """
    Announcements sent via Web Push to subscribed users.
    """
    title = models.CharField(max_length=150)
    body = models.TextField()
    url = models.CharField(max_length=255, default="/")
    sent_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Broadcast Notification"
        verbose_name_plural = "Broadcast Notifications"

    def __str__(self):
        return f"{self.title} ({self.sent_count} sent)"


# ==============================================================================
# BLOG & ACADEMICS (Exam Routine & Result System)
# ==============================================================================

class BlogPost(models.Model):
    """
    Academy Blog, Articles, Educational Insights, and Stories.
    """
    CATEGORY_CHOICES = [
        ("ACADEMIC", "Academic Insights & Study Tips"),
        ("STUDENT_LIFE", "Student Life & Extra-Curriculars"),
        ("COMMUNITY", "Community, Culture & Celebrations"),
        ("STEM", "Science, Tech & Computer Literacy"),
        ("PARENTING", "Parenting & Child Development"),
    ]

    title = models.CharField(max_length=250)
    slug = models.SlugField(max_length=270, unique=True, blank=True)
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES, default="ACADEMIC")
    author_name = models.CharField(max_length=120, default="Hunainath Editorial Team")
    author_role = models.CharField(max_length=120, default="Faculty Member")
    featured_image = models.ImageField(upload_to="blog/", blank=True, null=True)
    summary = models.TextField(help_text="Short teaser paragraph for cards")
    content = models.TextField(help_text="Full blog post content with paragraphs")
    is_published = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    views_count = models.PositiveIntegerField(default=0)
    published_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-published_at"]
        verbose_name = "Blog Post"
        verbose_name_plural = "Blog Posts"

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.title) or "post"
            candidate = base
            idx = 1
            while BlogPost.objects.filter(slug=candidate).exclude(pk=self.pk).exists():
                candidate = f"{base}-{idx}"
                idx += 1
            self.slug = candidate
        super().save(*args, **kwargs)


class ExamRoutine(models.Model):
    """
    Published Exam Routine & Timetable by Grade/Term.
    """
    TERM_CHOICES = [
        ("FIRST_TERMINAL", "First Terminal Examination"),
        ("MID_TERM", "Mid-Term Examination"),
        ("SECOND_TERMINAL", "Second Terminal Examination"),
        ("ANNUAL", "Annual / Final Examination (BLE Grade 8)"),
    ]

    title = models.CharField(max_length=200, help_text="e.g., Annual Board Examination Routine 2082 B.S.")
    exam_term = models.CharField(max_length=30, choices=TERM_CHOICES, default="ANNUAL")
    academic_year = models.CharField(max_length=20, default="2082 B.S.")
    grade = models.CharField(max_length=50, help_text="e.g. Grade 1 - 8, or Grade 8 (BLE)")
    start_date = models.DateField(help_text="Exam commencement date")
    end_date = models.DateField(help_text="Exam completion date")
    routine_file = models.FileField(upload_to="academics/routines/", blank=True, null=True, help_text="PDF or Image of full timetable")
    instructions = models.TextField(blank=True, default="1. Students must arrive 15 minutes before exam starts.\n2. Admit card and complete school uniform mandatory.\n3. Electronic devices and cheat sheets strictly prohibited.")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-academic_year", "start_date"]
        verbose_name = "Exam Routine"
        verbose_name_plural = "Exam Routines"

    def __str__(self):
        return f"{self.title} - {self.grade} ({self.academic_year})"


class ExamResult(models.Model):
    """
    Student Examination Marks & GPA Ledger.
    Allows parents/students to query results by Roll No & DOB or Symbol No.
    """
    TERM_CHOICES = [
        ("FIRST_TERMINAL", "First Terminal Examination"),
        ("MID_TERM", "Mid-Term Examination"),
        ("SECOND_TERMINAL", "Second Terminal Examination"),
        ("ANNUAL", "Annual / Final Examination (BLE Grade 8)"),
    ]

    student_name = models.CharField(max_length=150)
    symbol_number = models.CharField(max_length=50, unique=True, help_text="Unique Roll / Symbol Number e.g. HNA-801")
    date_of_birth = models.DateField(help_text="Student Date of Birth for verification")
    grade = models.CharField(max_length=30, help_text="Class e.g. Grade 8, Grade 7")
    academic_year = models.CharField(max_length=20, default="2082 B.S.")
    exam_term = models.CharField(max_length=30, choices=TERM_CHOICES, default="ANNUAL")
    
    # Performance summary
    gpa = models.DecimalField(max_digits=3, decimal_places=2, help_text="e.g. 3.85")
    grade_letter = models.CharField(max_length=5, default="A+", help_text="A+, A, B+, B, C+")
    rank = models.PositiveIntegerField(blank=True, null=True, help_text="Class position if applicable")
    total_marks = models.DecimalField(max_digits=6, decimal_places=1, default=0)
    result_status = models.CharField(max_length=20, default="PASSED", choices=[("PASSED", "Passed"), ("WITHHELD", "Withheld"), ("FAILED", "Needs Improvement")])
    remarks = models.CharField(max_length=255, blank=True, default="Outstanding academic performance.")

    # Breakdown JSON or multi-line text (Subject: Grade)
    subject_marks = models.TextField(
        default="Nepali: 3.6 (A)\nEnglish: 4.0 (A+)\nMathematics: 3.8 (A+)\nScience & Tech: 3.9 (A+)\nSocial Studies: 3.7 (A)\nHealth & PE: 4.0 (A+)\nMoral & Creative Arts: 4.0 (A+)",
        help_text="Enter 'Subject: Grade/Marks' per line",
    )
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-academic_year", "grade", "-gpa"]
        verbose_name = "Exam Result"
        verbose_name_plural = "Exam Results"

    def __str__(self):
        return f"{self.student_name} ({self.symbol_number}) - {self.grade} GPA: {self.gpa}"

    def get_subject_list(self):
        rows = []
        for line in self.subject_marks.splitlines():
            line = line.strip()
            if ":" in line:
                sub, val = line.split(":", 1)
                rows.append({"subject": sub.strip(), "score": val.strip()})
        return rows

