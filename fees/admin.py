from django.contrib import admin
from .models import FeeHead, FeeStructure, FeeComponent, Concession

from .models import (
    FeeHead,
    FeeStructure,
    FeeComponent,
    Concession,
    Invoice,
    Installment,
)


@admin.register(FeeHead)
class FeeHeadAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "is_active",
        "created_at",
    )

    list_filter = (
        "is_active",
    )

    search_fields = (
        "name",
        "description",
    )

    readonly_fields = (
        "created_at",
    )


class FeeComponentInline(admin.TabularInline):
    model = FeeComponent

    extra = 1

    min_num = 1

    fields = (
        "fee_head",
        "amount",
    )


@admin.register(FeeStructure)
class FeeStructureAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "course",
        "semester",
        "academic_year",
        "is_active",
        "display_total",
        "created_at",
    )

    list_filter = (
        "is_active",
        "course",
        "semester",
        "academic_year",
    )

    search_fields = (
        "name",
        "course",
        "academic_year",
    )

    readonly_fields = (
        "created_at",
    )

    inlines = [
        FeeComponentInline,
    ]

    def display_total(self, obj):
        return f"₹ {obj.total_amount:,.2f}"

    display_total.short_description = "Total Amount"


@admin.register(FeeComponent)
class FeeComponentAdmin(admin.ModelAdmin):
    list_display = (
        "fee_structure",
        "fee_head",
        "amount",
    )

    list_filter = (
        "fee_head",
        "fee_structure",
    )

    search_fields = (
        "fee_structure__name",
        "fee_head__name",
    )

@admin.register(Concession)
class ConcessionAdmin(admin.ModelAdmin):
    list_display = (
        "student",
        "fee_component",
        "concession_type",
        "value",
        "status",
        "approved_by",
        "created_at",
        "approved_at",
    )

    list_filter = (
        "status",
        "concession_type",
        "created_at",
    )

    search_fields = (
        "student__student_id",
        "student__name",
        "fee_component__fee_head__name",
    )

    readonly_fields = (
        "created_at",
        "approved_at",
    )

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):

    list_display = (
        "invoice_number",
        "student",
        "fee_structure",
        "gross_amount",
        "discount_amount",
        "net_amount",
        "due_date",
        "status",
        "created_at",
    )

    list_filter = (
        "status",
        "due_date",
        "created_at",
    )

    search_fields = (
        "invoice_number",
        "student__student_id",
        "student__name",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

@admin.register(Installment)
class InstallmentAdmin(admin.ModelAdmin):

    list_display = (
        "invoice",
        "installment_number",
        "amount",
        "due_date",
        "status",
    )

    list_filter = (
        "status",
        "due_date",
    )

    search_fields = (
        "invoice__invoice_number",
        "invoice__student__student_id",
        "invoice__student__name",
    )