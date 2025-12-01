from django.contrib import admin

from .models import Course, Enrollment


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("code", "title", "semester", "credits", "capacity")
    search_fields = ("code", "title", "semester")
    list_filter = ("semester",)


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ("student", "course", "enrolled_at")
    list_filter = ("enrolled_at",)
    search_fields = ("student__username", "student__email", "course__title", "course__code")
