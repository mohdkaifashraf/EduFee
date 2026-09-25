from django.conf import settings
from django.db import models


class Student(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "ACTIVE", "Active"
        INACTIVE = "INACTIVE", "Inactive"
        GRADUATED = "GRADUATED", "Graduated"

    student_id = models.CharField(
        max_length=30,
        unique=True,
        db_index=True,
    )

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="student_profile",
    )

    name = models.CharField(
        max_length=150,
    )

    email = models.EmailField(
        max_length=254,
    )

    phone = models.CharField(
        max_length=20,
        blank=True,
    )

    course = models.CharField(
        max_length=100,
    )

    department = models.CharField(
        max_length=100,
    )

    semester = models.PositiveSmallIntegerField()

    academic_year = models.CharField(
        max_length=20,
    )

    status = models.CharField(
        max_length=20,
        choices=Status,
        default=Status.ACTIVE,
        db_index=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = ["student_id"]
        permissions = [
            (
                "view_all_students",
                "Can view all students",
            ),
        ]

    def __str__(self):
        return f"{self.student_id} - {self.name}"