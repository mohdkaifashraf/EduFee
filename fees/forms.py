from django import forms

from .models import Concession, FeeComponent, FeeHead, Invoice, Installment


class FeeHeadForm(forms.ModelForm):

    class Meta:
        model = FeeHead

        fields = (
            "name",
            "description",
            "is_active",
        )

        widgets = {
            "description": forms.Textarea(
                attrs={
                    "rows": 4,
                    "placeholder": (
                        "Describe what this fee covers..."
                    ),
                }
            ),
        }

    def clean_name(self):
        name = self.cleaned_data["name"].strip()

        if not name:
            raise forms.ValidationError(
                "Fee head name cannot be empty."
            )

        return name

class ConcessionForm(forms.ModelForm):

    class Meta:
        model = Concession

        fields = (
            "student",
            "fee_component",
            "concession_type",
            "value",
            "reason",
        )

        widgets = {
            "reason": forms.Textarea(
                attrs={
                    "rows": 4,
                    "placeholder": "Enter the reason for this concession...",
                }
            ),
        }

    def clean(self):
        cleaned_data = super().clean()

        return cleaned_data

class InvoiceForm(forms.ModelForm):

    class Meta:
        model = Invoice

        fields = (
            "student",
            "fee_structure",
            "due_date",
        )

        widgets = {
            "due_date": forms.DateInput(
                attrs={
                    "type": "date",
                }
            ),
        }

    def clean(self):
        cleaned_data = super().clean()

        student = cleaned_data.get("student")
        fee_structure = cleaned_data.get("fee_structure")

        if student and fee_structure:

            if not fee_structure.is_active:
                raise forms.ValidationError(
                    "The selected fee structure is inactive."
                )

        return cleaned_data

class InstallmentForm(forms.Form):

    amount = forms.DecimalField(
        max_digits=12,
        decimal_places=2,
        min_value=0.01,
        widget=forms.NumberInput(
            attrs={
                "step": "0.01",
                "placeholder": "Enter amount",
            }
        ),
    )

    due_date = forms.DateField(
        widget=forms.DateInput(
            attrs={
                "type": "date",
            }
        )
    )