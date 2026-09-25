from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

from .models import Student


User = get_user_model()


class StudentCreateForm(UserCreationForm):
    name = forms.CharField(
        max_length=150,
        label="Student Name",
    )

    email = forms.EmailField(
        label="Student Email",
    )

    phone = forms.CharField(
        max_length=20,
        required=False,
    )

    student_id = forms.CharField(
        max_length=30,
        label="Student ID",
    )

    course = forms.CharField(
        max_length=100,
    )

    department = forms.CharField(
        max_length=100,
    )

    semester = forms.IntegerField(
        min_value=1,
        max_value=20,
    )

    academic_year = forms.CharField(
        max_length=20,
        initial="2026-27",
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = (
            "username",
            "email",
            "password1",
            "password2",
        )

    def clean_student_id(self):
        student_id = self.cleaned_data["student_id"].strip().upper()

        if Student.objects.filter(student_id=student_id).exists():
            raise forms.ValidationError(
                "A student with this Student ID already exists."
            )

        return student_id

    def save(self, commit=True):
        user = super().save(commit=False)

        user.first_name = self.cleaned_data["name"]
        user.email = self.cleaned_data["email"]

        if commit:
            user.save()

            Student.objects.create(
                user=user,
                student_id=self.cleaned_data["student_id"],
                name=self.cleaned_data["name"],
                email=self.cleaned_data["email"],
                phone=self.cleaned_data["phone"],
                course=self.cleaned_data["course"],
                department=self.cleaned_data["department"],
                semester=self.cleaned_data["semester"],
                academic_year=self.cleaned_data["academic_year"],
            )

        return user


class StudentUpdateForm(forms.ModelForm):

    class Meta:
        model = Student

        fields = (
            "student_id",
            "name",
            "email",
            "phone",
            "course",
            "department",
            "semester",
            "academic_year",
            "status",
        )

        widgets = {
            "student_id": forms.TextInput(
                attrs={
                    "readonly": True,
                }
            ),
        }

    def clean_student_id(self):
        return self.instance.student_id