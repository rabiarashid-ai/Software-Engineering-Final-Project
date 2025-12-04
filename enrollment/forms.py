from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Course


class StudentSignUpForm(UserCreationForm):
    ROLE_CHOICES = (
        ("student", "Student"),
        ("admin", "Admin"),
    )

    role = forms.ChoiceField(
        choices=ROLE_CHOICES,
        widget=forms.RadioSelect,
        initial="student",
        label="Account type",
    )
    email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(attrs={"class": "form-control", "placeholder": "you@example.com"}),
    )

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2", "role")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            existing_classes = field.widget.attrs.get("class", "")
            field.widget.attrs["class"] = f"{existing_classes} form-control".strip()
            field.widget.attrs.setdefault("placeholder", field.label)

        # Radio inputs need bootstrap styling
        self.fields["role"].widget.attrs["class"] = "form-check-input"

        # Remove password help text and loosen requirements visuals
        self.fields["password1"].help_text = ""
        self.fields["password2"].help_text = ""

    def save(self, commit=True):
        user = super().save(commit=False)
        selected_role = self.cleaned_data.get("role", "student")
        user.is_staff = selected_role == "admin"
        user.is_superuser = False
        if commit:
            user.save()
        return user

    def clean_password2(self):
        """
        Override default to skip Django's password validators and only check match.
        """
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("The two password fields didn’t match.")
        return password2


class CourseFilterForm(forms.Form):
    semester = forms.CharField(
        required=False,
        label="Semester",
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "e.g. Fall 2025"}),
    )
    search = forms.CharField(
        required=False,
        label="Search",
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Code, title, or description"}),
    )


class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ["code", "title", "description", "semester", "credits", "capacity"]
        widgets = {
            "code": forms.TextInput(attrs={"class": "form-control", "placeholder": "CS101"}),
            "title": forms.TextInput(attrs={"class": "form-control", "placeholder": "Intro to CS"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 4, "placeholder": "What students will learn"}),
            "semester": forms.TextInput(attrs={"class": "form-control", "placeholder": "Fall 2025"}),
            "credits": forms.NumberInput(attrs={"class": "form-control", "min": 0}),
            "capacity": forms.NumberInput(attrs={"class": "form-control", "min": 0}),
        }
