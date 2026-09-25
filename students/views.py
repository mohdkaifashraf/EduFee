from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.db import transaction
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render

from accounts.permissions import (
    ACCOUNTS_GROUP,
    STUDENT_GROUP,
    is_accounts_staff,
    is_student,
    role_required,
)

from .forms import StudentCreateForm, StudentUpdateForm
from .models import Student


@login_required
def student_list(request):
    if not is_accounts_staff(request.user):
        raise Http404

    students = Student.objects.select_related(
        "user"
    ).all()

    return render(
        request,
        "students/student_list.html",
        {
            "students": students,
        },
    )


@login_required
@role_required(is_accounts_staff)
def student_create(request):

    if request.method == "POST":
        form = StudentCreateForm(request.POST)

        if form.is_valid():

            with transaction.atomic():
                user = form.save()

                student_group, _ = Group.objects.get_or_create(
                    name=STUDENT_GROUP
                )

                user.groups.add(student_group)

            messages.success(
                request,
                "Student account created successfully.",
            )

            return redirect("student_list")

    else:
        form = StudentCreateForm()

    return render(
        request,
        "students/student_form.html",
        {
            "form": form,
            "page_heading": "Add Student",
            "submit_text": "Create Student",
        },
    )


@login_required
def student_detail(request, pk):

    student = get_object_or_404(
        Student.objects.select_related("user"),
        pk=pk,
    )

    if is_accounts_staff(request.user):
        pass

    elif (
        is_student(request.user)
        and student.user_id == request.user.id
    ):
        pass

    else:
        raise Http404

    return render(
        request,
        "students/student_detail.html",
        {
            "student": student,
            "can_edit": is_accounts_staff(request.user),
        },
    )


@login_required
@role_required(is_accounts_staff)
def student_update(request, pk):

    student = get_object_or_404(
        Student,
        pk=pk,
    )

    if request.method == "POST":

        form = StudentUpdateForm(
            request.POST,
            instance=student,
        )

        if form.is_valid():
            form.save()

            messages.success(
                request,
                "Student information updated successfully.",
            )

            return redirect(
                "student_detail",
                pk=student.pk,
            )

    else:
        form = StudentUpdateForm(
            instance=student,
        )

    return render(
        request,
        "students/student_form.html",
        {
            "form": form,
            "page_heading": "Edit Student",
            "submit_text": "Save Changes",
        },
    )
