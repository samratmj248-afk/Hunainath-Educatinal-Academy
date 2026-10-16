"""
Seed command to populate Shree Hunainath Educational Academy with authentic,
rich data including School Profile, Academic Programs, Notices, Faculty,
Testimonials, sample applications, and an admin superuser.
"""

from datetime import date
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import (
    SchoolProfile,
    AcademicProgram,
    Notice,
    FacultyMember,
    Testimonial,
    AdmissionApplication,
    ContactInquiry,
)


class Command(BaseCommand):
    help = "Seed database with authentic school data and superuser"

    def handle(self, *args, **options):
        self.stdout.write("Seeding Shree Hunainath Educational Academy data...")

        # 1. Superuser
        if not User.objects.filter(username="admin").exists():
            User.objects.create_superuser("admin", "admin@hunainath.edu.np", "HunainathAdmin2026!")
            self.stdout.write(self.style.SUCCESS("Superuser 'admin' created with password 'HunainathAdmin2026!'"))
        else:
            self.stdout.write("Superuser 'admin' already exists.")

        # 2. School Profile
        profile, created = SchoolProfile.objects.get_or_create(
            id=1,
            defaults={
                "name": "Shree Hunainath Educational Academy",
                "name_nepali": "श्री हुनैनाथ एजुकेशनल एकेडेमी",
                "tagline": "Empowering Minds, Inspiring Futures • ज्ञान, संस्कार र उत्कृष्टता",
                "established_year": 2008,
                "affiliation": "National Examination Board (NEB) & Ministry of Education, Nepal",
                "phone": "+977-99-402120",
                "mobile": "+977-9848712345",
                "email": "info@hunainath.edu.np",
                "address": "Shuklaphanta Municipality-5, Garjamani, Kanchanpur, Sudurpashchim Province, Nepal",
                "google_maps_url": "https://maps.google.com/?q=Shuklaphanta+Garjamani+Kanchanpur+Nepal",
                "facebook_url": "https://www.facebook.com/share/19ytNZhk3i/",
                "youtube_url": "https://www.youtube.com",
                "whatsapp_number": "+9779848712345",
                "principal_name": "Padam Raj Joshi",
                "principal_designation": "Principal & Academic Director",
                "principal_message": (
                    "Namaste and warm greetings from Shree Hunainath Educational Academy. Since our establishment in "
                    "Garjamani, Shuklaphanta, our unwavering objective has been to build an institution where scholastic "
                    "rigor meets sound moral character. We believe that true education does not simply impart textbook facts, "
                    "but ignites curiosity, builds resilience, and prepares youth to make honorable contributions to society. "
                    "With our modern STEM labs, smart classrooms, sports arenas, and devoted teaching staff, every student "
                    "at Hunainath is encouraged to discover their true brilliance."
                ),
                "about_text": (
                    "Shree Hunainath Educational Academy is a premier co-educational institution located in Shuklaphanta-5, "
                    "Garjamani, Kanchanpur. Serving families across Sudurpashchim Province, the academy provides quality "
                    "foundational, primary, and secondary education. With a proven track record of 100% success in SEE board "
                    "examinations, modern digital learning facilities, and diverse co-curricular activities, Hunainath stands "
                    "as a beacon of academic excellence in Kanchanpur."
                ),
                "mission": "To provide transformative, student-centered education blending rigorous academic disciplines with moral values, digital fluency, and cultural appreciation.",
                "vision": "To nurture self-disciplined, compassionate, and visionary future leaders capable of excelling in global academia and community advancement.",
                "stats_students": 1250,
                "stats_faculty": 52,
                "stats_pass_rate": "100%",
                "stats_years_excellence": 18,
            },
        )
        self.stdout.write(self.style.SUCCESS("School Profile verified."))

        # 3. Academic Programs
        programs_data = [
            {
                "title": "Early Childhood Education (ECE)",
                "level": "ECE",
                "grade_span": "Playgroup, Nursery, LKG & UKG",
                "short_summary": "Child-centric Montessori foundation with joyful phonics, sensory learning, and creative play.",
                "detailed_curriculum": (
                    "Our ECE wing provides a warm, stimulating environment where toddlers transition smoothly from home to school. "
                    "Curriculum focuses on psychomotor skills, linguistic fundamentals (Nepali & English phonetics), basic numeracy, "
                    "rhythm, music, painting, and social habits through play-based methods."
                ),
                "icon": "fa-shapes",
                "order": 1,
                "features_list": "Play-way & Montessori Methodology\nColorful Safe Child Play Area\nNutritious Meal Guidance\nCaring & Certified ECE Mentors\nParent-Child Orientation Sessions",
            },
            {
                "title": "Primary School Program",
                "level": "PRIMARY",
                "grade_span": "Grade 1 to Grade 5",
                "short_summary": "Strong core grounding in languages, mathematics, general science, and creative arts.",
                "detailed_curriculum": (
                    "Primary education at Hunainath balances concept mastery with experiential learning. Children develop English "
                    "communication confidence, mental arithmetic, computational thinking, social awareness, and ethical values through "
                    "storytelling, library visits, and hands-on science activities."
                ),
                "icon": "fa-book-reader",
                "order": 2,
                "features_list": "Bilingual Instruction (English & Nepali)\nSmart Interactive Classrooms\nDedicated Reading & Art Corner\nWeekly Sports & Physical Drills\nContinuous Diagnostic Assessment",
            },
            {
                "title": "Lower Secondary Level",
                "level": "LOWER_SEC",
                "grade_span": "Grade 6 to Grade 8",
                "short_summary": "In-depth scientific inquiry, computer programming basics, and critical thinking.",
                "detailed_curriculum": (
                    "Transitioning into abstract reasoning and deeper scientific investigation. Students participate in laboratory "
                    "demonstrations, computer lab practicals (typing, office suites, coding fundamentals), public speaking, "
                    "inter-house quiz competitions, and leadership activities."
                ),
                "icon": "fa-microscope",
                "order": 3,
                "features_list": "Practical Science Lab Experiments\nHands-on Computer Lab Classes\nInter-House Debates & Quizzes\nScouts & Junior Red Cross Activities\nRegular Formative Unit Assessments",
            },
        ]

        for p_info in programs_data:
            AcademicProgram.objects.get_or_create(
                title=p_info["title"],
                defaults=p_info,
            )
        self.stdout.write(self.style.SUCCESS("Academic programs seeded."))

        # 4. Notices
        notices_data = [
            {
                "title": "Admissions Open for Academic Session 2082/2026 (Playgroup to Grade 8)",
                "category": "ADMISSION",
                "priority": "HIGH",
                "is_ticker": True,
                "content": (
                    "Shree Hunainath Educational Academy cordially announces the opening of new admissions for the "
                    "Academic Session 2082/2026 from Playgroup to Grade 8. Limited seats available in each section "
                    "to maintain optimal student-teacher ratio. Parents can apply online via our website or visit the "
                    "administrative office in Garjamani between 9:00 AM to 4:00 PM."
                ),
            },
            {
                "title": "BLE Grade 8 Municipal Pre-Board Examination Routine Published",
                "category": "EXAM",
                "priority": "HIGH",
                "is_ticker": True,
                "content": (
                    "All students of Grade 8 (BLE board batch) are hereby notified that the Pre-Board Examination "
                    "commences shortly. Practical examinations for Science and Computer "
                    "will take place in their designated lab slots. Admit cards will be distributed from the exam controller desk."
                ),
            },
            {
                "title": "Annual Science, Robotics & Art Exhibition 2026 - Invitation to Parents",
                "category": "EVENT",
                "priority": "NORMAL",
                "is_ticker": True,
                "content": (
                    "We are delighted to invite all parents, guardians, and education enthusiasts to our Annual Science & "
                    "Creative Arts Exhibition. Students from Primary to Secondary will showcase live models, renewable energy "
                    "demonstrations, software projects, and handicraft art."
                ),
            },
            {
                "title": "Parent-Teacher Conference (PTC) & Progress Report Card Distribution",
                "category": "ACADEMIC",
                "priority": "NORMAL",
                "is_ticker": False,
                "content": (
                    "The Second Terminal Parent-Teacher Meeting will be held this Saturday from 10:00 AM to 2:00 PM. Parents "
                    "are requested to interact with class mentors to review student performance and personal development milestones."
                ),
            },
            {
                "title": "Inter-House Football & Athletics Tournament Results",
                "category": "EVENT",
                "priority": "NORMAL",
                "is_ticker": False,
                "content": (
                    "Congratulations to Sagarmatha House for clinching the Champion Trophy at the Annual Inter-House Sports "
                    "Championship! Special recognition to all athletes for exemplifying discipline, fair play, and athletic spirit."
                ),
            },
        ]

        for n_info in notices_data:
            Notice.objects.get_or_create(
                title=n_info["title"],
                defaults=n_info,
            )
        self.stdout.write(self.style.SUCCESS("Notices seeded."))

        # 5. Faculty Members
        faculty_data = [
            {
                "name": "Padam Raj Joshi",
                "designation": "Principal & Academic Director",
                "department": "ADMIN",
                "qualification": "M.Ed. (Curriculum & Instruction), B.Sc.",
                "bio": "Over 20 years of distinguished experience in educational leadership, curriculum development, and school governance in Sudurpashchim.",
                "is_leadership": True,
                "order": 1,
            },
            {
                "name": "Birendra Singh Dhami",
                "designation": "Vice Principal & Exam Controller",
                "department": "ADMIN",
                "qualification": "M.Sc. Physics, B.Ed.",
                "bio": "Dedicated educator specializing in secondary physics, national examination coordination, and discipline management.",
                "is_leadership": True,
                "order": 2,
            },
            {
                "name": "Ramesh Prasad Bhatta",
                "designation": "Senior Mathematics Coordinator",
                "department": "MATHS",
                "qualification": "M.Sc. Mathematics",
                "bio": "Renowned for simplifying complex mathematical concepts, nurturing logical inquiry, and training students for competitive math olympiads.",
                "is_leadership": False,
                "order": 3,
            },
            {
                "name": "Sita Kumari Bist",
                "designation": "Head of Science & Practical Labs",
                "department": "SCIENCE",
                "qualification": "M.Sc. Chemistry, B.Ed.",
                "bio": "Passionate about lab safety, experiential chemistry experiments, and guiding student entries in district science exhibitions.",
                "is_leadership": False,
                "order": 4,
            },
            {
                "name": "Nirmala Rawal",
                "designation": "Senior English Faculty & Literary Club Lead",
                "department": "LANGUAGES",
                "qualification": "M.A. English Literature",
                "bio": "Champions communicative English fluency, debate coaching, elocution competitions, and school journal publications.",
                "is_leadership": False,
                "order": 5,
            },
            {
                "name": "Sunita Chaudhary",
                "designation": "ECE Coordinator & Primary Section Incharge",
                "department": "PRIMARY",
                "qualification": "B.Ed. (Early Childhood Care & Development)",
                "bio": "Expert in child psychology, joyful Montessori pedagogy, phonetics, and creating supportive classrooms for early learners.",
                "is_leadership": False,
                "order": 6,
            },
            {
                "name": "Mahesh Bahadur Chand",
                "designation": "Physical Education & Athletics Coach",
                "department": "SPORTS",
                "qualification": "Bachelor in Physical Education (B.P.Ed.)",
                "bio": "Former regional athlete promoting physical fitness, football, volleyball, karate training, and sportsmanship.",
                "is_leadership": False,
                "order": 7,
            },
        ]

        for f_info in faculty_data:
            FacultyMember.objects.get_or_create(
                name=f_info["name"],
                defaults=f_info,
            )
        self.stdout.write(self.style.SUCCESS("Faculty members seeded."))

        # 6. Testimonials
        testimonials_data = [
            {
                "name": "Devendra Bahadur Saund",
                "role": "Parent of Class 8 Student",
                "quote": (
                    "Sending our son to Shree Hunainath Academy is the best educational decision we made. The teachers "
                    "are genuinely caring, the science lab practicals are top-notch, and the disciplined environment has "
                    "transformed his confidence."
                ),
                "rating": 5,
                "order": 1,
            },
            {
                "name": "Pooja Paneru",
                "role": "SEE Distinction Holder (GPA 3.90)",
                "quote": (
                    "Hunainath Academy provided me with strong mathematical foundations and constant motivation. The extra coaching "
                    "and mock tests made the board examinations completely stress-free. I am proud to be a Hunainath alumna!"
                ),
                "rating": 5,
                "order": 2,
            },
            {
                "name": "Ganesh Raj Pant",
                "role": "Guardian & Community Member",
                "quote": (
                    "The focus on moral character, Nepali cultural values, alongside modern English fluency sets Hunainath "
                    "apart. Shuklaphanta has truly benefited from having such a premier school right in our community."
                ),
                "rating": 5,
                "order": 3,
            },
        ]

        for t_info in testimonials_data:
            Testimonial.objects.get_or_create(
                name=t_info["name"],
                defaults=t_info,
            )
        self.stdout.write(self.style.SUCCESS("Testimonials seeded."))

        # 7. Sample Admission Application & Inquiries (for live dashboard metrics)
        if not AdmissionApplication.objects.exists():
            AdmissionApplication.objects.create(
                student_name="Aayush Joshi",
                date_of_birth=date(2013, 5, 14),
                gender="MALE",
                grade_applying_for="Grade 6",
                previous_school="Garjamani Basic School",
                previous_gpa="3.75",
                parent_name="Khadak Bahadur Joshi",
                parent_phone="+977-9848799887",
                parent_email="khadak.joshi@example.com",
                parent_occupation="Agriculture & Business",
                address="Shuklaphanta-5, Garjamani, Kanchanpur",
                additional_notes="Interested in school football team and computer club.",
                status="PENDING",
            )
            self.stdout.write(self.style.SUCCESS("Sample application created."))

        if not ContactInquiry.objects.exists():
            ContactInquiry.objects.create(
                name="Deepak Thapa",
                email="deepak.thapa@example.com",
                phone="+977-9812345678",
                subject="Inquiry regarding Grade 1 School Bus Route & Timings",
                message="Hello, I would like to inquire about the school transport route coverage around Garjamani and Jhalari for newly enrolled students.",
                is_read=False,
            )
            self.stdout.write(self.style.SUCCESS("Sample inquiry created."))

        self.stdout.write(self.style.SUCCESS("[SUCCESS] All database seed operations completed successfully!"))
