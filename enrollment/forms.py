from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Course


class StudentSignUpForm(UserCreationForm):
    email = forms.EmailField(required=False)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")


class CourseFilterForm(forms.Form):
    semester = forms.CharField(required=False, label="Semester")
    search = forms.CharField(required=False, label="Search")


class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ["code", "title", "description", "semester", "credits", "capacity"]
