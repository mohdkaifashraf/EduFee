from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.forms import formset_factory
from django.core.exceptions import ValidationError
from django.forms import formset_factory

from accounts.permissions import is_accounts_staff, is_admin, role_required

from .forms import FeeHeadForm, InvoiceForm
from .models import Concession, FeeHead, Invoice
from .services import create_invoice
from .forms import (
    FeeHeadForm,
    InvoiceForm,
    ConcessionForm,
    InstallmentForm,
)


@login_required
@role_required(is_admin)
def fee_head_list(request):
    fee_heads = FeeHead.objects.all()

    return render(
        request,
        "fees/fee_head_list.html",
        {
            "fee_heads": fee_heads,
        },
    )


@login_required
@role_required(is_admin)
def fee_head_create(request):
    if request.method == "POST":
        form = FeeHeadForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(
                request,
                "Fee head created successfully.",
            )
            return redirect("fee_head_list")
    else:
        form = FeeHeadForm()

    return render(
        request,
        "fees/fee_head_form.html",
        {
            "form": form,
        },
    )


@login_required
@role_required(is_accounts_staff)
def concession_list(request):
    concessions = (
        Concession.objects
        .select_related(
            "student",
            "fee_component",
            "fee_component__fee_head",
            "fee_component__fee_structure",
            "approved_by",
        )
        .all()
    )

    return render(
        request,
        "fees/concession_list.html",
        {
            "concessions": concessions,
        },
    )


@login_required
@role_required(is_accounts_staff)
def concession_create(request):
    from .forms import ConcessionForm

    if request.method == "POST":
        form = ConcessionForm(request.POST)

        if form.is_valid():
            concession = form.save()

            messages.success(
                request,
                "Concession request created successfully.",
            )

            return redirect("concession_list")
    else:
        form = ConcessionForm()

    return render(
        request,
        "fees/concession_form.html",
        {
            "form": form,
        },
    )


@login_required
@role_required(is_accounts_staff)
def concession_detail(request, pk):
    concession = get_object_or_404(
        Concession.objects.select_related(
            "student",
            "fee_component",
            "fee_component__fee_head",
            "fee_component__fee_structure",
            "approved_by",
        ),
        pk=pk,
    )

    return render(
        request,
        "fees/concession_detail.html",
        {
            "concession": concession,
        },
    )


@login_required
@role_required(is_accounts_staff)
@transaction.atomic
def concession_approve(request, pk):
    if request.method != "POST":
        return redirect("concession_detail", pk=pk)

    concession = get_object_or_404(
        Concession.objects.select_for_update(),
        pk=pk,
    )

    if concession.status != Concession.Status.PENDING:
        messages.error(
            request,
            "Only pending concessions can be approved.",
        )
        return redirect("concession_detail", pk=pk)

    concession.status = Concession.Status.APPROVED
    concession.approved_by = request.user
    concession.approved_at = timezone.now()
    concession.save(
        update_fields=[
            "status",
            "approved_by",
            "approved_at",
        ]
    )

    messages.success(
        request,
        "Concession approved successfully.",
    )

    return redirect("concession_detail", pk=pk)


@login_required
@role_required(is_accounts_staff)
@transaction.atomic
def concession_reject(request, pk):
    if request.method != "POST":
        return redirect("concession_detail", pk=pk)

    concession = get_object_or_404(
        Concession.objects.select_for_update(),
        pk=pk,
    )

    if concession.status != Concession.Status.PENDING:
        messages.error(
            request,
            "Only pending concessions can be rejected.",
        )
        return redirect("concession_detail", pk=pk)

    concession.status = Concession.Status.REJECTED
    concession.save(update_fields=["status"])

    messages.success(
        request,
        "Concession rejected.",
    )

    return redirect("concession_detail", pk=pk)


@login_required
@role_required(is_accounts_staff)
@transaction.atomic
def concession_cancel(request, pk):
    if request.method != "POST":
        return redirect("concession_detail", pk=pk)

    concession = get_object_or_404(
        Concession.objects.select_for_update(),
        pk=pk,
    )

    if concession.status not in (
        Concession.Status.PENDING,
        Concession.Status.APPROVED,
    ):
        messages.error(
            request,
            "This concession cannot be cancelled.",
        )
        return redirect("concession_detail", pk=pk)

    concession.status = Concession.Status.CANCELLED
    concession.save(update_fields=["status"])

    messages.success(
        request,
        "Concession cancelled successfully.",
    )

    return redirect("concession_detail", pk=pk)

@login_required
@role_required(is_accounts_staff)
def invoice_list(request):

    invoices = (
        Invoice.objects
        .select_related(
            "student",
            "fee_structure",
        )
        .all()
    )

    return render(
        request,
        "fees/invoice_list.html",
        {
            "invoices": invoices,
        },
    )

@login_required
@role_required(is_accounts_staff)
def invoice_create(request):

    if request.method == "POST":

        form = InvoiceForm(request.POST)

        if form.is_valid():

            invoice = create_invoice(
                student=form.cleaned_data["student"],
                fee_structure=form.cleaned_data["fee_structure"],
                due_date=form.cleaned_data["due_date"],
            )

            messages.success(
                request,
                f"Invoice {invoice.invoice_number} created successfully.",
            )

            return redirect(
                "invoice_detail",
                pk=invoice.pk,
            )

    else:

        form = InvoiceForm()

    return render(
        request,
        "fees/invoice_form.html",
        {
            "form": form,
        },
    )

@login_required
@role_required(is_accounts_staff)
def invoice_detail(request, pk):

    invoice = get_object_or_404(
        Invoice.objects.select_related(
            "student",
            "fee_structure",
        ),
        pk=pk,
    )

    components = invoice.fee_structure.components.select_related(
        "fee_head"
    )

    return render(
        request,
        "fees/invoice_detail.html",
        {
            "invoice": invoice,
            "components": components,
        },
    )

@login_required
@role_required(is_accounts_staff)
def installment_create(request, invoice_id):

    invoice = get_object_or_404(
        Invoice,
        pk=invoice_id,
    )

    if invoice.installments.exists():
        messages.error(
            request,
            "Installments already exist for this invoice.",
        )
        return redirect(
            "invoice_detail",
            pk=invoice.pk,
        )

    InstallmentFormSet = formset_factory(
        InstallmentForm,
        extra=1,
        min_num=1,
        validate_min=True,
    )

    if request.method == "POST":

        formset = InstallmentFormSet(
            request.POST,
            prefix="installments",
        )

        if formset.is_valid():

            installment_data = [
                {
                    "amount": form.cleaned_data["amount"],
                    "due_date": form.cleaned_data["due_date"],
                }
                for form in formset
            ]

            try:

                create_installments(
                    invoice,
                    installment_data,
                )

                messages.success(
                    request,
                    "Installments created successfully.",
                )

                return redirect(
                    "invoice_detail",
                    pk=invoice.pk,
                )

            except ValidationError as error:

                error_message = str(error)

    else:

        formset = InstallmentFormSet(
            prefix="installments",
        )

    return render(
        request,
        "fees/installment_form.html",
        {
            "invoice": invoice,
            "formset": formset,
        },
    )   
