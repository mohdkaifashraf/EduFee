from decimal import Decimal
from django.core.exceptions import ValidationError
from .models import Concession
from django.db import transaction
from django.utils import timezone
from .models import Invoice, Installment


def calculate_invoice_amounts(student, fee_structure):
    """
    Calculate invoice amounts from the fee structure
    and approved concessions.
    """

    components = fee_structure.components.select_related(
        "fee_head"
    )

    gross_amount = sum(
        (
            component.amount
            for component in components
        ),
        Decimal("0.00"),
    )

    discount_amount = Decimal("0.00")

    for component in components:

        approved_concessions = Concession.objects.filter(
            student=student,
            fee_component=component,
            status=Concession.Status.APPROVED,
        )

        for concession in approved_concessions:

            if (
                concession.concession_type
                == Concession.ConcessionType.FIXED
            ):
                discount = concession.value

            else:
                discount = (
                    component.amount
                    * concession.value
                    / Decimal("100")
                )

            discount_amount += discount

    if discount_amount > gross_amount:
        raise ValidationError(
            "Total concession cannot exceed the gross fee."
        )

    net_amount = gross_amount - discount_amount

    return {
        "gross_amount": gross_amount,
        "discount_amount": discount_amount,
        "net_amount": net_amount,
    }

def generate_invoice_number():
    year = timezone.now().year

    last_invoice = (
        Invoice.objects
        .filter(invoice_number__startswith=f"INV-{year}-")
        .order_by("-id")
        .first()
    )

    if last_invoice:
        last_number = int(
            last_invoice.invoice_number.split("-")[-1]
        )
        next_number = last_number + 1
    else:
        next_number = 1

    return f"INV-{year}-{next_number:06d}"

def create_invoice(student, fee_structure, due_date):
    amounts = calculate_invoice_amounts(
        student,
        fee_structure,
    )

    return Invoice.objects.create(
        invoice_number=generate_invoice_number(),
        student=student,
        fee_structure=fee_structure,
        due_date=due_date,
        **amounts,
    )

def validate_installment_total(invoice, installments):
    """
    Ensure the total of the proposed installments
    exactly equals the invoice net amount.
    """

    total = sum(
        (
            installment["amount"]
            for installment in installments
        ),
        Decimal("0.00"),
    )

    if total != invoice.net_amount:
        raise ValidationError(
            f"Installment total must equal invoice "
            f"net amount of ₹{invoice.net_amount:.2f}. "
            f"Current total is ₹{total:.2f}."
        )

    return True

def create_installments(invoice, installment_data):
    """
    Create installments for an invoice after validating
    that their total exactly equals the invoice net amount.
    """

    if invoice.installments.exists():
        raise ValidationError(
            "Installments already exist for this invoice."
        )

    validate_installment_total(
        invoice,
        installment_data,
    )

    installments = []

    with transaction.atomic():

        for index, data in enumerate(
            installment_data,
            start=1,
        ):

            installment = Installment.objects.create(
                invoice=invoice,
                installment_number=index,
                amount=data["amount"],
                due_date=data["due_date"],
                status=Installment.Status.PENDING,
            )

            installments.append(installment)

    return installments