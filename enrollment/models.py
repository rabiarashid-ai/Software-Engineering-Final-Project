from django.conf import settings
from django.db import models


class Course(models.Model):
    code = models.CharField(max_length=20)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    semester = models.CharField(max_length=50)
    credits = models.PositiveIntegerField(default=0)
    capacity = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["code"]

    def __str__(self) -> str:
        return f"{self.code} - {self.title}"

    @property
    def enrolled_count(self) -> int:
        return self.enrollments.count()

    @property
    def seats_remaining(self) -> int:
        return max(self.capacity - self.enrolled_count, 0)


class Enrollment(models.Model):
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="enrollments",
    )
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="enrollments")
    enrolled_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-enrolled_at"]
        constraints = [
            models.UniqueConstraint(fields=["student", "course"], name="unique_student_course_enrollment"),
        ]

    def __str__(self) -> str:
        return f"{self.student.username} -> {self.course.code}"

    @property
    def user(self):
        """Backward compatibility alias; prefer .student."""
        return self.student
