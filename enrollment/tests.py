from django.contrib.auth.models import User
from django.db import IntegrityError
from django.test import Client, TestCase
from django.urls import reverse

from .models import Course, Enrollment


class EnrollmentFlowTests(TestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(username="student", password="pass12345")
        self.course = Course.objects.create(title="Test Course")

    def test_user_can_enroll(self) -> None:
        client = Client()
        client.login(username="student", password="pass12345")
        response = client.post(reverse("course_detail", args=[self.course.pk]), {"action": "enroll"})
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Enrollment.objects.filter(user=self.user, course=self.course).exists())

    def test_duplicate_enrollment_prevented(self) -> None:
        Enrollment.objects.create(user=self.user, course=self.course)
        second = Enrollment(user=self.user, course=self.course)
        with self.assertRaises(IntegrityError):
            second.save()
