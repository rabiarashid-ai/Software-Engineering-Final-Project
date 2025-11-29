from django.urls import path

from . import views

urlpatterns = [
    path("", views.course_list, name="course_list"),
    path("courses/create/", views.course_create, name="course_create"),
    path("courses/<int:pk>/", views.course_detail, name="course_detail"),
    path("courses/<int:pk>/edit/", views.course_edit, name="course_edit"),
    path("courses/<int:pk>/delete/", views.course_delete, name="course_delete"),
    path("my-courses/", views.my_courses, name="my_courses"),
    path("signup/", views.signup, name="signup"),
]
