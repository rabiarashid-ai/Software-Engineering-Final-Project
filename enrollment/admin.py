from django.contrib import admin

from .models import Course, Enrollment


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("title", "instructor", "start_date", "end_date", "capacity")
    search_fields = ("title", "instructor")
    list_filter = ("start_date", "end_date")


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ("user", "course", "enrolled_at")
    list_filter = ("enrolled_at",)
    search_fields = ("user__username", "user__email", "course__title")
#just to test commit