from django.contrib import admin

from .models import Student


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = (
        "student_id",
        "name",
        "course",
        "department",
        "semester",
        "academic_year",
        "status",
        "created_at",
    )

    list_filter = (
        "status",
        "course",
        "department",
        "academic_year",
    )

    search_fields = (
        "student_id",
        "name",
        "email",
        "phone",
    )

    ordering = (
        "student_id",
    )

    readonly_fields = (
        "created_at",
    )