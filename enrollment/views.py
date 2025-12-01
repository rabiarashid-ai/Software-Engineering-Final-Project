from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Q
from django.http import HttpRequest, HttpResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CourseFilterForm, CourseForm, StudentSignUpForm
from .models import Course, Enrollment


@login_required
def course_list(request: HttpRequest) -> HttpResponse:
    courses = Course.objects.all()
    form = CourseFilterForm(request.GET or None)
    if form.is_valid():
        semester = form.cleaned_data.get("semester")
        search = form.cleaned_data.get("search")
        if semester:
            courses = courses.filter(semester__icontains=semester)
        if search:
            courses = courses.filter(
                Q(code__icontains=search)
                | Q(title__icontains=search)
                | Q(description__icontains=search)
            )

    enrolled_courses = set(
        Enrollment.objects.filter(student=request.user).values_list("course_id", flat=True)
    )
    return render(
        request,
        "enrollment/course_list.html",
        {"courses": courses, "form": form, "enrolled_courses": enrolled_courses},
    )


@login_required
def course_detail(request: HttpRequest, pk: int) -> HttpResponse:
    course = get_object_or_404(Course, pk=pk)
    is_enrolled = Enrollment.objects.filter(student=request.user, course=course).exists()
    return render(
        request,
        "enrollment/course_detail.html",
        {"course": course, "is_enrolled": is_enrolled},
    )


@login_required
def enroll_course(request: HttpRequest, pk: int) -> HttpResponse:
    course = get_object_or_404(Course, pk=pk)
    if course.seats_remaining > 0:
        Enrollment.objects.get_or_create(student=request.user, course=course)
    return redirect("course_detail", pk=course.pk)


@login_required
def drop_course(request: HttpRequest, pk: int) -> HttpResponse:
    course = get_object_or_404(Course, pk=pk)
    Enrollment.objects.filter(student=request.user, course=course).delete()
    return redirect("course_detail", pk=course.pk)


@user_passes_test(lambda u: u.is_staff, login_url="login")
def add_course(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = CourseForm(request.POST)
        if form.is_valid():
            course = form.save()
            return redirect("course_detail", pk=course.pk)
    else:
        form = CourseForm()
    return render(request, "enrollment/course_form.html", {"form": form})


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
    enrollments = Enrollment.objects.filter(student=request.user).select_related("course")
    return render(request, "enrollment/my_courses.html", {"enrollments": enrollments})


def signup(request: HttpRequest) -> HttpResponse:
    if request.user.is_authenticated:
        return redirect("course_list")

    if request.method == "POST":
        form = StudentSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Account created and signed in.")
            return redirect("course_list")
    else:
        form = StudentSignUpForm()
    return render(request, "enrollment/signup.html", {"form": form})
