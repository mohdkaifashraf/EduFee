from django.conf import settings
from django.db import models


class FeeHead(models.Model):
    name = models.CharField(
        max_length=100,
        unique=True,
    )

    description = models.TextField(
        blank=True,
    )

    is_active = models.BooleanField(
        default=True,
        db_index=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = ["name"]
        verbose_name = "Fee Head"
        verbose_name_plural = "Fee Heads"

    def __str__(self):
        return self.name

class FeeStructure(models.Model):
    name = models.CharField(
        max_length=150,
    )

    course = models.CharField(
        max_length=100,
    )

    semester = models.PositiveSmallIntegerField(
        help_text="Semester number, for example 1, 2, 3, etc.",
    )

    academic_year = models.CharField(
        max_length=20,
    )

    is_active = models.BooleanField(
        default=True,
        db_index=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = [
            "-academic_year",
            "course",
            "semester",
        ]

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "course",
                    "semester",
                    "academic_year",
                ],
                name="unique_fee_structure_per_academic_context",
            ),
        ]

        verbose_name = "Fee Structure"
        verbose_name_plural = "Fee Structures"

    def __str__(self):
        return self.name

    @property
    def total_amount(self):
        return sum(
            (
                component.amount
                for component in self.components.all()
            ),
            0,
        )

class FeeComponent(models.Model):
    fee_structure = models.ForeignKey(
        FeeStructure,
        on_delete=models.PROTECT,
        related_name="components",
    )

    fee_head = models.ForeignKey(
        FeeHead,
        on_delete=models.PROTECT,
        related_name="components",
    )

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
    )

    class Meta:
        ordering = ["fee_head__name"]

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "fee_structure",
                    "fee_head",
                ],
                name="unique_fee_head_per_structure",
            ),

            models.CheckConstraint(
                condition=models.Q(amount__gt=0),
                name="fee_component_amount_positive",
            ),
        ]

        verbose_name = "Fee Component"
        verbose_name_plural = "Fee Components"

    def __str__(self):
        return (
            f"{self.fee_structure.name} - "
            f"{self.fee_head.name}"
        )

class Concession(models.Model):

    class ConcessionType(models.TextChoices):
        FIXED = "FIXED", "Fixed Amount"
        PERCENTAGE = "PERCENTAGE", "Percentage"

    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        APPROVED = "APPROVED", "Approved"
        REJECTED = "REJECTED", "Rejected"
        CANCELLED = "CANCELLED", "Cancelled"

    student = models.ForeignKey(
        "students.Student",
        on_delete=models.PROTECT,
        related_name="concessions",
    )

    fee_component = models.ForeignKey(
        FeeComponent,
        on_delete=models.PROTECT,
        related_name="concessions",
    )

    concession_type = models.CharField(
        max_length=20,
        choices=ConcessionType,
    )

    value = models.DecimalField(
        max_digits=12,
        decimal_places=2,
    )

    reason = models.TextField()

    status = models.CharField(
        max_length=20,
        choices=Status,
        default=Status.PENDING,
        db_index=True,
    )

    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="approved_concessions",
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)

    approved_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    class Meta:
        ordering = ["-created_at"]

    def clean(self):
        from django.core.exceptions import ValidationError

        if self.value <= 0:
            raise ValidationError({
                "value": "Concession value must be greater than zero."
            })

        if self.concession_type == self.ConcessionType.PERCENTAGE:
            if self.value > 100:
                raise ValidationError({
                    "value": "Percentage concession cannot exceed 100%."
                })

        if (
            self.concession_type == self.ConcessionType.FIXED
            and self.fee_component_id
            and self.value > self.fee_component.amount
        ):
            raise ValidationError({
                "value": "Fixed concession cannot exceed the fee component amount."
            })

    def __str__(self):
        return (
            f"{self.student.student_id} - "
            f"{self.fee_component.fee_head.name} - "
            f"{self.value}"
        )

class Invoice(models.Model):

    class Status(models.TextChoices):
        DRAFT = "DRAFT", "Draft"
        ISSUED = "ISSUED", "Issued"
        PARTIALLY_PAID = "PARTIALLY_PAID", "Partially Paid"
        PAID = "PAID", "Paid"
        OVERDUE = "OVERDUE", "Overdue"
        CANCELLED = "CANCELLED", "Cancelled"

    invoice_number = models.CharField(
        max_length=30,
        unique=True,
        db_index=True,
    )

    student = models.ForeignKey(
        "students.Student",
        on_delete=models.PROTECT,
        related_name="invoices",
    )

    fee_structure = models.ForeignKey(
        FeeStructure,
        on_delete=models.PROTECT,
        related_name="invoices",
    )

    gross_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
    )

    discount_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
    )

    net_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
    )

    due_date = models.DateField()

    status = models.CharField(
        max_length=20,
        choices=Status,
        default=Status.DRAFT,
        db_index=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.invoice_number} - {self.student.name}"


class Installment(models.Model):

    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        PARTIALLY_PAID = "PARTIALLY_PAID", "Partially Paid"
        PAID = "PAID", "Paid"
        OVERDUE = "OVERDUE", "Overdue"

    invoice = models.ForeignKey(
        Invoice,
        on_delete=models.PROTECT,
        related_name="installments",
    )

    installment_number = models.PositiveSmallIntegerField()

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
    )

    due_date = models.DateField()

    status = models.CharField(
        max_length=20,
        choices=Status,
        default=Status.PENDING,
        db_index=True,
    )

    class Meta:
        ordering = ["installment_number"]

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "invoice",
                    "installment_number",
                ],
                name="unique_installment_number_per_invoice",
            ),

            models.CheckConstraint(
                condition=models.Q(amount__gt=0),
                name="installment_amount_positive",
            ),
        ]

    def __str__(self):
        return (
            f"{self.invoice.invoice_number} - "
            f"Installment {self.installment_number}"
        )