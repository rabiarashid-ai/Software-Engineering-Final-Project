from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from .forms import CourseForm, SignUpForm
from .models import Course, Enrollment


def course_list(request: HttpRequest) -> HttpResponse:
    courses = Course.objects.all()
    return render(request, "enrollment/course_list.html", {"courses": courses})


def course_detail(request: HttpRequest, pk: int) -> HttpResponse:
    course = get_object_or_404(Course, pk=pk)
    is_enrolled = False
    if request.user.is_authenticated:
        is_enrolled = Enrollment.objects.filter(user=request.user, course=course).exists()

    if request.method == "POST":
        if not request.user.is_authenticated:
            messages.error(request, "Please log in to enroll.")
            return redirect(f"{reverse('login')}?next={request.path}")

        if request.POST.get("action") == "enroll" and not is_enrolled:
            if course.capacity and course.enrollments.count() >= course.capacity:
                messages.error(request, "This course is full.")
            else:
                Enrollment.objects.get_or_create(user=request.user, course=course)
                messages.success(request, "Enrolled successfully.")
            return redirect("course_detail", pk=course.pk)

        if request.POST.get("action") == "unenroll" and is_enrolled:
            Enrollment.objects.filter(user=request.user, course=course).delete()
            messages.info(request, "You have unenrolled from this course.")
            return redirect("course_detail", pk=course.pk)

    return render(
        request,
        "enrollment/course_detail.html",
        {"course": course, "is_enrolled": is_enrolled},
    )


@login_required
def course_create(request: HttpRequest) -> HttpResponse:
    if not request.user.is_staff:
        return HttpResponseForbidden("Only staff can create courses.")

    if request.method == "POST":
        form = CourseForm(request.POST)
        if form.is_valid():
            course = form.save()
            messages.success(request, "Course created.")
            return redirect("course_detail", pk=course.pk)
    else:
        form = CourseForm()
    return render(request, "enrollment/course_form.html", {"form": form, "is_edit": False})


@login_required
def course_edit(request: HttpRequest, pk: int) -> HttpResponse:
    if not request.user.is_staff:
        return HttpResponseForbidden("Only staff can edit courses.")

    course = get_object_or_404(Course, pk=pk)
    if request.method == "POST":
        form = CourseForm(request.POST, instance=course)
        if form.is_valid():
            form.save()
            messages.success(request, "Course updated.")
            return redirect("course_detail", pk=course.pk)
    else:
        form = CourseForm(instance=course)
    return render(request, "enrollment/course_form.html", {"form": form, "is_edit": True, "course": course})


@login_required
def course_delete(request: HttpRequest, pk: int) -> HttpResponse:
    if not request.user.is_staff:
        return HttpResponseForbidden("Only staff can delete courses.")

    course = get_object_or_404(Course, pk=pk)
    if request.method == "POST":
        course.delete()
        messages.info(request, "Course deleted.")
        return redirect("course_list")
    return render(request, "enrollment/course_detail.html", {"course": course})


@login_required
def my_courses(request: HttpRequest) -> HttpResponse:
    enrollments = Enrollment.objects.filter(user=request.user).select_related("course")
    courses = [enrollment.course for enrollment in enrollments]
    return render(request, "enrollment/my_courses.html", {"courses": courses})


def signup(request: HttpRequest) -> HttpResponse:
    if request.user.is_authenticated:
        return redirect("course_list")

    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Account created and signed in.")
            return redirect("course_list")
    else:
        form = SignUpForm()
    return render(request, "enrollment/signup.html", {"form": form})
