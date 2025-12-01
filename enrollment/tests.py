from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.db.utils import IntegrityError

from .models import Course, Enrollment
from .forms import StudentSignUpForm, CourseFilterForm, CourseForm


# ============================
#  MODEL TESTS (BACKEND)
# ============================

class CourseModelTests(TestCase):
    def setUp(self):
        self.course = Course.objects.create(
            code="ITC101",
            title="Intro to CS",
            description="Basic course",
            semester="Fall 2025",
            credits=3,
            capacity=2,
        )

    def test_course_str(self):
        """__str__ should return 'code - title'"""
        self.assertEqual(str(self.course), "ITC101 - Intro to CS")

    def test_enrolled_count_and_seats_remaining(self):
        """enrolled_count and seats_remaining should update correctly."""
        user1 = User.objects.create_user(username="student1", password="pass12345")
        user2 = User.objects.create_user(username="student2", password="pass12345")

        # No enrollments at first
        self.assertEqual(self.course.enrolled_count, 0)
        self.assertEqual(self.course.seats_remaining, 2)

        # Enroll first student
        Enrollment.objects.create(student=user1, course=self.course)
        self.assertEqual(self.course.enrolled_count, 1)
        self.assertEqual(self.course.seats_remaining, 1)

        # Enroll second student
        Enrollment.objects.create(student=user2, course=self.course)
        self.assertEqual(self.course.enrolled_count, 2)
        self.assertEqual(self.course.seats_remaining, 0)


class EnrollmentModelTests(TestCase):
    def setUp(self):
        self.course = Course.objects.create(
            code="ITC102",
            title="Algorithms",
            semester="Spring 2026",
            credits=3,
            capacity=30,
        )
        self.user = User.objects.create_user(username="student", password="pass12345")

    def test_enrollment_str(self):
        """__str__ should return 'username -> course_code'."""
        enrollment = Enrollment.objects.create(student=self.user, course=self.course)
        self.assertEqual(str(enrollment), "student -> ITC102")

    def test_unique_student_course_pair(self):
        """A student cannot enroll in the same course twice (unique_together)."""
        Enrollment.objects.create(student=self.user, course=self.course)

        with self.assertRaises(IntegrityError):
            Enrollment.objects.create(student=self.user, course=self.course)


# ============================
#  AUTH & SIGNUP VIEW TESTS
# ============================

class SignupViewTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_signup_get(self):
        """GET /enrollment/signup/ should return the signup form."""
        url = reverse('signup')
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'enrollment/signup.html')
        self.assertIsInstance(response.context['form'], StudentSignUpForm)

    def test_signup_post_creates_user_and_redirects(self):
        """POST valid data should create a user and redirect to course_list."""
        url = reverse('signup')
        data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password1": "StrongPass123!",
            "password2": "StrongPass123!",
        }
        response = self.client.post(url, data)

        # user should be created
        self.assertTrue(User.objects.filter(username="newuser").exists())
        # redirect to course list
        self.assertRedirects(response, reverse('course_list'))


# ============================
#  BACKEND VIEW TESTS
# ============================

class CourseViewsTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="student", password="pass12345")

        # Some sample courses
        self.course1 = Course.objects.create(
            code="MTH101",
            title="Calculus I",
            semester="Fall 2025",
            credits=3,
            capacity=2,
        )
        self.course2 = Course.objects.create(
            code="MTH102",
            title="Calculus II",
            semester="Spring 2026",
            credits=3,
            capacity=1,
        )

    def test_course_list_requires_login(self):
        """Anonymous user should be redirected to login page."""
        url = reverse('course_list')
        response = self.client.get(url)

        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login/", response.url)

    def test_course_list_shows_courses_for_logged_in_user(self):
        """Logged-in user should see list of courses."""
        self.client.force_login(self.user)
        url = reverse('course_list')
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'enrollment/course_list.html')
        # both course titles should appear
        content = response.content.decode()
        self.assertIn("Calculus I", content)
        self.assertIn("Calculus II", content)

    def test_course_list_filter_by_semester_and_search(self):
        """Filtering by semester and search should work."""
        self.client.force_login(self.user)
        url = reverse('course_list')

        # Filter by semester 'Fall'
        response = self.client.get(url, {"semester": "Fall"})
        content = response.content.decode()
        self.assertIn("Calculus I", content)
        self.assertNotIn("Calculus II", content)

        # Filter by search '102'
        response = self.client.get(url, {"search": "102"})
        content = response.content.decode()
        self.assertIn("Calculus II", content)
        self.assertNotIn("Calculus I", content)

    def test_course_detail_view(self):
        """Course detail page should show course info and enrollment state."""
        self.client.force_login(self.user)
        url = reverse('course_detail', kwargs={"pk": self.course1.pk})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'enrollment/course_detail.html')
        content = response.content.decode()
        self.assertIn("Calculus I", content)

    def test_enroll_course_success(self):
        """User can enroll in a course with free seats."""
        self.client.force_login(self.user)
        url = reverse('enroll_course', kwargs={"pk": self.course1.pk})

        response = self.client.post(url)
        self.assertRedirects(response, reverse('course_detail', kwargs={"pk": self.course1.pk}))

        # Enrollment created
        self.assertTrue(
            Enrollment.objects.filter(student=self.user, course=self.course1).exists()
        )

    def test_enroll_course_when_full(self):
        """If course is full, user should not be enrolled."""
        other = User.objects.create_user(username="other", password="pass12345")
        # capacity = 1 for course2
        Enrollment.objects.create(student=other, course=self.course2)

        self.client.force_login(self.user)
        url = reverse('enroll_course', kwargs={"pk": self.course2.pk})

        response = self.client.post(url)
        self.assertRedirects(response, reverse('course_detail', kwargs={"pk": self.course2.pk}))

        # user should NOT be enrolled
        self.assertFalse(
            Enrollment.objects.filter(student=self.user, course=self.course2).exists()
        )

    def test_drop_course(self):
        """User can drop a course if enrolled."""
        Enrollment.objects.create(student=self.user, course=self.course1)
        self.client.force_login(self.user)

        url = reverse('drop_course', kwargs={"pk": self.course1.pk})
        response = self.client.post(url)
        self.assertRedirects(response, reverse('course_detail', kwargs={"pk": self.course1.pk}))

        self.assertFalse(
            Enrollment.objects.filter(student=self.user, course=self.course1).exists()
        )

    def test_my_courses_view(self):
        """my_courses should list only the logged-in student's enrollments."""
        Enrollment.objects.create(student=self.user, course=self.course1)
        other = User.objects.create_user(username="other", password="pass12345")
        Enrollment.objects.create(student=other, course=self.course2)

        self.client.force_login(self.user)
        url = reverse('my_courses')
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'enrollment/my_courses.html')

        enrollments = response.context['enrollments']
        # Only one enrollment, for course1
        self.assertEqual(enrollments.count(), 1)
        self.assertEqual(enrollments.first().course, self.course1)


# ============================
#  ADMIN / STAFF VIEW TESTS
# ============================

class StaffCourseCreationTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.staff = User.objects.create_user(
            username="staff",
            password="pass12345",
            is_staff=True,
        )
        self.student = User.objects.create_user(
            username="student",
            password="pass12345",
            is_staff=False,
        )

    def test_add_course_requires_login(self):
        url = reverse('add_course')
        response = self.client.get(url)

        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login/", response.url)

    def test_non_staff_cannot_access_add_course(self):
        self.client.force_login(self.student)
        url = reverse('add_course')
        response = self.client.get(url)

        # user_passes_test redirects to login with ?next=...
        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login/", response.url)

    def test_staff_can_create_course(self):
        self.client.force_login(self.staff)
        url = reverse('add_course')
        data = {
            "code": "CS200",
            "title": "Software Engineering",
            "description": "Test course",
            "semester": "Fall 2026",
            "credits": 3,
            "capacity": 40,
        }

        response = self.client.post(url, data)
        course = Course.objects.get(code="CS200")
        self.assertRedirects(response, reverse('course_detail', kwargs={"pk": course.pk}))


# ============================
#  FRONTEND / TEMPLATE TESTS
# ============================

class FrontendTemplateTests(TestCase):
    """
    These tests focus on what the user sees:
    - Main headings
    - Important UI text
    - Basic structure of the pages
    """

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="student", password="pass12345")
        self.course = Course.objects.create(
            code="ITC100",
            title="Test Frontend Course",
            semester="Fall 2025",
            credits=3,
            capacity=10,
        )

    def test_course_list_page_ui_elements(self):
        """Course list should show main heading and 'No courses' text if needed."""
        self.client.force_login(self.user)
        url = reverse('course_list')
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        content = response.content.decode()

        # Main title from course_list.html
        self.assertIn("Available Courses", content)
        # Filter form labels
        self.assertIn("Semester", content)
        self.assertIn("Search", content)

    def test_signup_page_ui_elements(self):
        """Signup page should show Create Account UI text."""
        url = reverse('signup')
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        content = response.content.decode()
        self.assertIn("Create Account", content)
        self.assertIn("Join our student enrollment system", content)

    def test_course_detail_page_ui_elements(self):
        """Course detail page should show code and title."""
        self.client.force_login(self.user)
        url = reverse('course_detail', kwargs={"pk": self.course.pk})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        content = response.content.decode()
        self.assertIn("Test Frontend Course", content)
        self.assertIn("ITC100", content)


# ============================
#  LOGOUT VIEW TESTS
# ============================

class LogoutViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="student", password="pass12345")

    def test_logout_view_logs_user_out(self):
        """Student logout should clear session and redirect to login."""
        self.client.force_login(self.user)
        url = reverse('logout')  # 'accounts/logout/' mapped in project urls
        response = self.client.get(url)

        self.assertRedirects(response, reverse('login'))
        # User should be logged out – no auth user id in session
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_admin_logout_redirect(self):
        """Admin logout view should redirect to admin login page."""
        self.client.force_login(self.user)
        url = reverse('admin_logout')
        response = self.client.get(url)

        self.assertEqual(response.status_code, 302)
        self.assertIn("/admin/login/?next=/admin/", response.url)
